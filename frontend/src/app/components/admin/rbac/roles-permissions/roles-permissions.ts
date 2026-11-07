import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Observable, catchError, forkJoin, of } from 'rxjs';
import { Button } from 'primeng/button';
import { InputText } from 'primeng/inputtext';
import { MultiSelect } from 'primeng/multiselect';
import { Select } from 'primeng/select';
import { Tag } from 'primeng/tag';

import { SessionStore } from '../../../../core/session';
import { stateLabel, stateSeverity } from '../../../../shared/state-severity';
import { RecordStatus, STATUS_OPTIONS } from '../../../../models/security/status';
import { RoleI } from '../../../../models/security/role';
import { ResourceI } from '../../../../models/security/resource';
import { ResourceRoleI } from '../../../../models/security/resource-role';
import { RoleUserI } from '../../../../models/security/role-user';
import { UserI } from '../../../../models/security/user';
import { RoleApi } from '../../../../services/security/role-api';
import { ResourceApi } from '../../../../services/security/resource-api';
import { ResourceRoleApi } from '../../../../services/security/resource-role-api';
import { RoleUserApi } from '../../../../services/security/role-user-api';
import { UserApi } from '../../../../services/security/user-api';
import {
  ACTIONS,
  Action,
  CellState,
  EntityRow,
  activeTargets,
  applyCell,
  buildEntityRows,
  cellState,
  diffSets,
  indexByRole,
} from '../rbac-matrix';

interface Option {
  label: string;
  value: number;
}

const ROLE_NAME_PATTERN = /^[A-Za-z][A-Za-z_]*$/;

@Component({
  selector: 'app-roles-permissions',
  standalone: true,
  imports: [FormsModule, Button, InputText, MultiSelect, Select, Tag],
  templateUrl: './roles-permissions.html',
  styleUrl: './roles-permissions.css',
})
export class RolesPermissions implements OnInit {
  private readonly roleApi = inject(RoleApi);
  private readonly resourceApi = inject(ResourceApi);
  private readonly resourceRoleApi = inject(ResourceRoleApi);
  private readonly roleUserApi = inject(RoleUserApi);
  private readonly userApi = inject(UserApi);
  private readonly session = inject(SessionStore);

  readonly statusOptions = STATUS_OPTIONS;
  readonly actions = ACTIONS;
  readonly stateLabel = stateLabel;
  readonly stateSeverity = stateSeverity;

  // Datos del servidor
  readonly roles = signal<RoleI[]>([]);
  readonly resources = signal<ResourceI[]>([]);
  readonly resourceRoles = signal<ResourceRoleI[]>([]);
  readonly roleUsers = signal<RoleUserI[]>([]);
  readonly users = signal<UserI[]>([]);

  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly saving = signal(false);
  readonly saveError = signal<string | null>(null);

  // Lista de roles
  readonly search = signal('');
  readonly filteredRoles = computed(() => {
    const q = this.search().trim().toLowerCase();
    return q ? this.roles().filter((r) => r.name.toLowerCase().includes(q)) : this.roles();
  });

  // Rol seleccionado y su borrador. "creating" es el modo de alta de un rol nuevo.
  readonly selectedId = signal<number | null>(null);
  readonly creating = signal(false);
  readonly selected = computed(() => this.roles().find((r) => r.id === this.selectedId()) ?? null);

  readonly draftName = signal('');
  readonly draftStatus = signal<RecordStatus>('ACTIVE');
  readonly draftUsers = signal<ReadonlySet<number>>(new Set());
  readonly draftGrants = signal<ReadonlySet<number>>(new Set());
  readonly draftUserList = computed(() => [...this.draftUsers()]);

  /** Snapshot del borrador tal como quedó al cargar el rol. Se compara para saber si hay cambios. */
  private readonly baseline = signal('');
  private readonly draftSnapshot = computed(() =>
    this.snapshot(this.draftName(), this.draftStatus(), this.draftUsers(), this.draftGrants()),
  );
  readonly dirty = computed(() => this.draftSnapshot() !== this.baseline());
  readonly nameValid = computed(() => {
    const name = this.draftName().trim();
    return name.length >= 2 && name.length <= 30 && ROLE_NAME_PATTERN.test(name);
  });

  // Opciones y matriz
  readonly entityRows = computed<EntityRow[]>(() => buildEntityRows(this.resources()));
  readonly userOptions = computed<Option[]>(() =>
    this.users().map((u) => ({ label: u.username, value: u.id })),
  );
  readonly grantCount = computed(() => this.draftGrants().size);

  // Permisos del usuario actual para habilitar cada parte
  readonly canCreateRole = computed(() => this.session.canPermission('POST /api/roles/'));
  readonly canEditRole = computed(() => this.session.canPermission('PATCH /api/roles/:id/'));
  readonly canDeleteRole = computed(() => this.session.canPermission('DELETE /api/roles/:id/'));
  readonly canEditGrants = computed(
    () =>
      this.session.canPermission('POST /api/resource-roles/') &&
      this.session.canPermission('DELETE /api/resource-roles/:id/'),
  );
  readonly canEditUsers = computed(
    () =>
      this.session.canPermission('POST /api/role-users/') &&
      this.session.canPermission('DELETE /api/role-users/:id/'),
  );

  private readonly failedSources: string[] = [];
  private pendingSelectId: number | null = null;

  ngOnInit(): void {
    this.load();
  }

  refresh(): void {
    if (this.dirty() && !confirm('Hay cambios sin guardar. ¿Descartarlos y recargar?')) return;
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.failedSources.length = 0;

    forkJoin({
      roles: this.safe(this.roleApi.getAll(), 'roles'),
      resources: this.safe(this.resourceApi.getAll(), 'recursos'),
      resourceRoles: this.safe(this.resourceRoleApi.getAll(), 'permisos por rol'),
      roleUsers: this.safe(this.roleUserApi.getAll(), 'asignaciones'),
      users: this.safe(this.userApi.getAll(), 'usuarios'),
    }).subscribe((data) => {
      this.roles.set(data.roles);
      this.resources.set(data.resources);
      this.resourceRoles.set(data.resourceRoles);
      this.roleUsers.set(data.roleUsers);
      this.users.set(data.users);
      this.loading.set(false);

      if (this.failedSources.length) {
        this.error.set(`No se pudieron cargar: ${this.failedSources.join(', ')}.`);
      }

      if (this.pendingSelectId !== null) {
        const id = this.pendingSelectId;
        this.pendingSelectId = null;
        this.selectRole(id, true);
      } else if (!this.creating()) {
        const current = this.selectedId();
        const stillExists = current !== null && data.roles.some((r) => r.id === current);
        const fallback = data.roles[0]?.id ?? null;
        this.selectRole(stillExists ? current : fallback, true);
      }
    });
  }

  selectRole(id: number | null, force = false): void {
    if (!force && this.dirty() && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
    this.creating.set(false);
    this.selectedId.set(id);
    const role = this.roles().find((r) => r.id === id);
    if (!role) {
      this.resetDraft('', 'ACTIVE', new Set(), new Set());
      return;
    }
    const users = activeTargets(this.roleUsers(), role.id, (a) => a.user);
    const grants = activeTargets(this.resourceRoles(), role.id, (g) => g.resource);
    this.resetDraft(role.name, role.status, users, grants);
  }

  startCreate(): void {
    if (this.dirty() && !confirm('Hay cambios sin guardar. ¿Descartarlos?')) return;
    this.creating.set(true);
    this.selectedId.set(null);
    this.resetDraft('', 'ACTIVE', new Set(), new Set());
  }

  setName(value: string): void {
    this.draftName.set(value);
  }

  setStatus(value: RecordStatus): void {
    this.draftStatus.set(value);
  }

  setUsers(ids: number[]): void {
    this.draftUsers.set(new Set(ids));
  }

  stateOf(row: EntityRow, action: Action): CellState {
    return cellState(row.ids[action], this.draftGrants());
  }

  toggleCell(ids: number[], on: boolean): void {
    this.draftGrants.set(applyCell(this.draftGrants(), ids, on));
  }

  toggleAll(on: boolean): void {
    let next: ReadonlySet<number> = new Set();
    if (on) {
      const all: number[] = [];
      for (const row of this.entityRows()) for (const a of ACTIONS) all.push(...row.ids[a.key]);
      next = new Set(all);
    }
    this.draftGrants.set(next);
  }

  usersOf(roleId: number): number {
    return activeTargets(this.roleUsers(), roleId, (a) => a.user).size;
  }

  grantsOf(roleId: number): number {
    return activeTargets(this.resourceRoles(), roleId, (g) => g.resource).size;
  }

  save(): void {
    if (!this.dirty() || this.saving()) return;
    if (!this.nameValid()) {
      this.saveError.set('El nombre debe tener de 2 a 30 letras o guion bajo, sin números.');
      return;
    }
    if (this.creating()) {
      this.createRole();
      return;
    }

    const role = this.selected();
    if (!role) return;

    const requests: Observable<unknown>[] = [];
    const name = this.draftName().trim().toUpperCase();
    const status = this.draftStatus();

    if (this.canEditRole() && (name !== role.name || status !== role.status)) {
      requests.push(this.roleApi.update(role.id, { name, status }));
    }

    if (this.canEditUsers()) {
      const initial = activeTargets(this.roleUsers(), role.id, (a) => a.user);
      const { add, remove } = diffSets(initial, this.draftUsers());
      const index = indexByRole(this.roleUsers(), role.id, (a) => a.user);
      for (const userId of add) {
        const existing = index.get(userId);
        requests.push(
          existing
            ? this.roleUserApi.update(existing.id, { status: 'ACTIVE' })
            : this.roleUserApi.create({ role: role.id, user: userId, status: 'ACTIVE' }),
        );
      }
      for (const userId of remove) {
        const existing = index.get(userId);
        if (existing?.status === 'ACTIVE') requests.push(this.roleUserApi.remove(existing.id));
      }
    }

    if (this.canEditGrants()) {
      const initial = activeTargets(this.resourceRoles(), role.id, (g) => g.resource);
      const { add, remove } = diffSets(initial, this.draftGrants());
      const index = indexByRole(this.resourceRoles(), role.id, (g) => g.resource);
      for (const resourceId of add) {
        const existing = index.get(resourceId);
        requests.push(
          existing
            ? this.resourceRoleApi.update(existing.id, { status: 'ACTIVE' })
            : this.resourceRoleApi.create({ resource: resourceId, role: role.id, status: 'ACTIVE' }),
        );
      }
      for (const resourceId of remove) {
        const existing = index.get(resourceId);
        if (existing?.status === 'ACTIVE') requests.push(this.resourceRoleApi.remove(existing.id));
      }
    }

    if (requests.length === 0) {
      this.saveError.set('No tienes permisos para cambiar este rol.');
      return;
    }

    this.saving.set(true);
    this.saveError.set(null);
    forkJoin(requests).subscribe({
      next: () => {
        this.saving.set(false);
        this.load();
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.saveError.set(this.describe(err));
        this.load();
      },
    });
  }

  removeRole(): void {
    const role = this.selected();
    if (!role) return;
    if (!confirm(`¿Dar de baja el rol ${role.name}? El registro se conserva como inactivo.`)) return;
    this.roleApi.remove(role.id).subscribe({
      next: () => {
        this.selectedId.set(null);
        this.load();
      },
      error: () => this.saveError.set('No se pudo dar de baja el rol.'),
    });
  }

  discard(): void {
    const role = this.selected();
    if (this.creating()) {
      this.creating.set(false);
      this.selectRole(this.roles()[0]?.id ?? null, true);
      return;
    }
    if (role) this.selectRole(role.id, true);
  }

  private createRole(): void {
    this.saving.set(true);
    this.saveError.set(null);
    this.roleApi
      .create({ name: this.draftName().trim().toUpperCase(), status: this.draftStatus() })
      .subscribe({
        next: (role) => {
          this.saving.set(false);
          this.pendingSelectId = role.id;
          this.creating.set(false);
          this.load();
        },
        error: (err: HttpErrorResponse) => {
          this.saving.set(false);
          this.saveError.set(this.describe(err));
        },
      });
  }

  private resetDraft(
    name: string,
    status: RecordStatus,
    users: ReadonlySet<number>,
    grants: ReadonlySet<number>,
  ): void {
    this.draftName.set(name);
    this.draftStatus.set(status);
    this.draftUsers.set(new Set(users));
    this.draftGrants.set(new Set(grants));
    this.baseline.set(this.snapshot(name, status, users, grants));
    this.saveError.set(null);
  }

  private snapshot(
    name: string,
    status: RecordStatus,
    users: ReadonlySet<number>,
    grants: ReadonlySet<number>,
  ): string {
    return JSON.stringify({
      name: name.trim(),
      status,
      users: [...users].sort((a, b) => a - b),
      grants: [...grants].sort((a, b) => a - b),
    });
  }

  /** Si una fuente falla, devuelve lista vacía y la deja anotada, para no tumbar toda la pantalla. */
  private safe<T>(source: Observable<T[]>, label: string): Observable<T[]> {
    return source.pipe(
      catchError(() => {
        this.failedSources.push(label);
        return of([] as T[]);
      }),
    );
  }

  private describe(err: HttpErrorResponse): string {
    const body = err.error;
    if (body && typeof body === 'object') {
      return Object.entries(body)
        .map(([campo, msgs]) => `${campo}: ${Array.isArray(msgs) ? msgs.join(' ') : msgs}`)
        .join(' · ');
    }
    return 'No se pudo guardar. Revisa que el backend esté corriendo.';
  }
}
