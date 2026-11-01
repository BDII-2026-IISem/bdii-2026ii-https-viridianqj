import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { RecordStatus, STATUS_OPTIONS } from '../../../../models/security/status';
import { ResourceRoleI, ResourceRolePayload } from '../../../../models/security/resource-role';
import { ResourceRoleApi } from '../../../../services/security/resource-role-api';
import { ResourceApi } from '../../../../services/security/resource-api';
import { RoleApi } from '../../../../services/security/role-api';
import { stateLabel, stateSeverity } from '../../../../shared/state-severity';

interface Option {
  label: string;
  value: number;
}

@Component({
  selector: 'app-resource-role-list',
  standalone: true,
  imports: [HasPermission, ReactiveFormsModule, TableModule, Button, Tag, Dialog, Select],
  templateUrl: './resource-role-list.html',
  styleUrl: './resource-role-list.css',
})
export class ResourceRoleList implements OnInit {
  private readonly service = inject(ResourceRoleApi);
  private readonly resourceService = inject(ResourceApi);
  private readonly roleService = inject(RoleApi);
  private readonly fb = inject(FormBuilder);

  readonly statusOptions = STATUS_OPTIONS;
  readonly stateLabel = stateLabel;
  readonly stateSeverity = stateSeverity;

  readonly items = signal<ResourceRoleI[]>([]);
  readonly resourceOptions = signal<Option[]>([]);
  readonly roleOptions = signal<Option[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly dialogOpen = signal(false);
  readonly editing = signal<ResourceRoleI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    resource: [0, [Validators.required, Validators.min(1)]],
    role: [0, [Validators.required, Validators.min(1)]],
    status: ['ACTIVE' as RecordStatus, Validators.required],
  });

  readonly rows = computed(() =>
    this.items().map((r) => ({
      ...r,
      resourceName: this.resourceLabel(r.resource),
      roleName: this.roleLabel(r.role),
    })),
  );

  ngOnInit(): void {
    this.loadAll();
  }

  loadAll(): void {
    this.loading.set(true);
    this.error.set(null);
    forkJoin({
      assignments: this.service.getAll(),
      resources: this.resourceService.getAll(),
      roles: this.roleService.getAll(),
    }).subscribe({
      next: ({ assignments, resources, roles }) => {
        this.items.set(assignments);
        this.resourceOptions.set(resources.map((r) => ({ label: `${r.method} ${r.route}`, value: r.id })));
        this.roleOptions.set(roles.map((r) => ({ label: r.name, value: r.id })));
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los permisos por rol.');
        this.loading.set(false);
      },
    });
  }

  resourceLabel(id: number): string {
    return this.resourceOptions().find((o) => o.value === id)?.label ?? `#${id}`;
  }

  roleLabel(id: number): string {
    return this.roleOptions().find((o) => o.value === id)?.label ?? `#${id}`;
  }

  openCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({ resource: 0, role: 0, status: 'ACTIVE' });
    this.dialogOpen.set(true);
  }

  openEdit(row: ResourceRoleI): void {
    this.editing.set(row);
    this.formError.set(null);
    this.form.reset({ resource: row.resource, role: row.role, status: row.status as RecordStatus });
    this.dialogOpen.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    const payload: ResourceRolePayload = { resource: v.resource, role: v.role, status: v.status };
    const current = this.editing();
    const request = current ? this.service.update(current.id, payload) : this.service.create(payload);

    this.saving.set(true);
    this.formError.set(null);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogOpen.set(false);
        this.loadAll();
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.formError.set(this.describe(err));
      },
    });
  }

  remove(row: ResourceRoleI): void {
    if (!confirm(`¿Quitar el permiso ${this.resourceLabel(row.resource)} al rol ${this.roleLabel(row.role)}?`)) return;
    this.service.remove(row.id).subscribe({
      next: () => this.loadAll(),
      error: () => this.error.set('No se pudo quitar el permiso.'),
    });
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
