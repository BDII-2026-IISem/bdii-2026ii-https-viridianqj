import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { InputText } from 'primeng/inputtext';
import { Password } from 'primeng/password';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';
import { Tooltip } from 'primeng/tooltip';
import { HasPermission } from '../../../../shared/directives/has-permission';
import { RecordStatus, STATUS_OPTIONS } from '../../../../models/security/status';
import { UserI, UserPayload, UserPermission } from '../../../../models/security/user';
import { UserApi } from '../../../../services/security/user-api';
import { stateLabel, stateSeverity } from '../../../../shared/state-severity';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [HasPermission, ReactiveFormsModule, TableModule, Button, Tag, Dialog, InputText, Password, Select, Tooltip],
  templateUrl: './user-list.html',
  styleUrl: './user-list.css',
})
export class UserList implements OnInit {
  private readonly service = inject(UserApi);
  private readonly fb = inject(FormBuilder);

  readonly statusOptions = STATUS_OPTIONS;
  readonly stateLabel = stateLabel;
  readonly stateSeverity = stateSeverity;

  readonly items = signal<UserI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    if (!q) return this.items();
    return this.items().filter((u) =>
      [u.username, u.email, u.firstName ?? '', u.lastName ?? ''].some((v) => v.toLowerCase().includes(q)),
    );
  });

  readonly dialogOpen = signal(false);
  readonly editing = signal<UserI | null>(null);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);

  readonly permOpen = signal(false);
  readonly permUser = signal<UserI | null>(null);
  readonly permissions = signal<UserPermission[]>([]);
  readonly permLoading = signal(false);
  readonly permError = signal<string | null>(null);

  readonly form = this.fb.nonNullable.group({
    username: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(150)]],
    email: ['', [Validators.required, Validators.email, Validators.maxLength(150)]],
    firstName: ['', [Validators.maxLength(150)]],
    lastName: ['', [Validators.maxLength(150)]],
    password: ['', [Validators.required, Validators.minLength(8)]],
    status: ['ACTIVE' as RecordStatus, Validators.required],
  });

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.getAll().subscribe({
      next: (rows) => {
        this.items.set(rows);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los usuarios.');
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.editing.set(null);
    this.formError.set(null);
    this.form.reset({ username: '', email: '', firstName: '', lastName: '', password: '', status: 'ACTIVE' });
    this.form.controls.password.enable();
    this.form.controls.password.setValidators([Validators.required, Validators.minLength(8)]);
    this.form.controls.password.updateValueAndValidity();
    this.dialogOpen.set(true);
  }

  openEdit(user: UserI): void {
    this.editing.set(user);
    this.formError.set(null);
    this.form.reset({
      username: user.username,
      email: user.email,
      firstName: user.firstName ?? '',
      lastName: user.lastName ?? '',
      password: '',
      status: user.status as RecordStatus,
    });
    this.form.controls.password.clearValidators();
    this.form.controls.password.disable();
    this.dialogOpen.set(true);
  }

  save(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    const v = this.form.getRawValue();
    const base = {
      username: v.username.trim(),
      email: v.email.trim(),
      firstName: v.firstName.trim(),
      lastName: v.lastName.trim(),
      status: v.status,
    };
    const current = this.editing();
    const payload: UserPayload = current ? base : { ...base, password: v.password };
    const request = current ? this.service.update(current.id, payload) : this.service.create(payload);

    this.saving.set(true);
    this.formError.set(null);
    request.subscribe({
      next: () => {
        this.saving.set(false);
        this.dialogOpen.set(false);
        this.load();
      },
      error: (err: HttpErrorResponse) => {
        this.saving.set(false);
        this.formError.set(this.describe(err));
      },
    });
  }

  remove(user: UserI): void {
    if (!confirm(`¿Dar de baja a ${user.username}? El registro se conserva como inactivo.`)) return;
    this.service.remove(user.id).subscribe({
      next: () => this.load(),
      error: () => this.error.set('No se pudo dar de baja el usuario.'),
    });
  }

  openPermissions(user: UserI): void {
    this.permUser.set(user);
    this.permissions.set([]);
    this.permError.set(null);
    this.permLoading.set(true);
    this.permOpen.set(true);
    this.service.permissions(user.id).subscribe({
      next: (rows) => {
        this.permissions.set(rows);
        this.permLoading.set(false);
      },
      error: () => {
        this.permError.set('No se pudieron cargar los permisos del usuario.');
        this.permLoading.set(false);
      },
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
