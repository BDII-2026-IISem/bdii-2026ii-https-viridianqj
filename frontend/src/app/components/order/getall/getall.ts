import { RouterLink } from '@angular/router';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { forkJoin } from 'rxjs';
import { Button } from 'primeng/button';
import { Dialog } from 'primeng/dialog';
import { InputNumber } from 'primeng/inputnumber';
import { Select } from 'primeng/select';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ClientI } from '../../../models/business/client';
import { OrderI } from '../../../models/business/order';
import { ProductI } from '../../../models/business/product';
import { ClientService } from '../../../services/business/client';
import { OrderPayload, OrderService } from '../../../services/business/order';
import { ProductService } from '../../../services/business/product';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';
import { DEFAULT_BRANCH_ID, DINING_TABLES } from '../../../shared/venue';

interface DraftLine {
  productId: number;
  name: string;
  unitPrice: number;
  quantity: number;
}

@Component({
  selector: 'app-getall',
  standalone: true,
  imports: [FormsModule, RouterLink, TableModule, Button, Tag, Dialog, Select, InputNumber, CurrencyPipe, DatePipe],
  templateUrl: './getall.html',
  styleUrl: './getall.css',
})
export class Getall implements OnInit {
  private readonly service = inject(OrderService);
  private readonly clientsApi = inject(ClientService);
  private readonly productsApi = inject(ProductService);

  readonly items = signal<OrderI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly dialogOpen = signal(false);
  readonly saving = signal(false);
  readonly formError = signal<string | null>(null);
  readonly lineError = signal<string | null>(null);

  readonly clients = signal<ClientI[]>([]);
  readonly products = signal<ProductI[]>([]);
  readonly tables = DINING_TABLES;
  readonly channels = [
    { label: 'Mesa', value: 'MESA' },
    { label: 'Recogida', value: 'RECOGIDA' },
    { label: 'Domicilio', value: 'DOMICILIO' },
  ];

  // Borrador en signals, como pide la guía (sin FormGroup)
  readonly clientId = signal<number | null>(null);
  readonly channel = signal<string>('RECOGIDA');
  readonly tableId = signal<number | null>(null);
  readonly productId = signal<number | null>(null);
  readonly quantity = signal<number>(1);
  readonly lines = signal<DraftLine[]>([]);

  readonly subtotal = computed(() =>
    this.lines().reduce((sum, l) => sum + l.unitPrice * l.quantity, 0),
  );
  readonly needsTable = computed(() => this.channel() === 'MESA');

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.getAll().subscribe({
      next: (data) => {
        this.items.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar pedidos. Revisa que el backend esté corriendo en el puerto 8000.');
        this.loading.set(false);
      },
    });
  }

  openCreate(): void {
    this.formError.set(null);
    this.lineError.set(null);
    this.clientId.set(null);
    this.channel.set('RECOGIDA');
    this.tableId.set(null);
    this.productId.set(null);
    this.quantity.set(1);
    this.lines.set([]);

    forkJoin({ clients: this.clientsApi.getAll(), products: this.productsApi.getAll() }).subscribe({
      next: ({ clients, products }) => {
        this.clients.set(clients.filter((c) => c.status === 'ACTIVE'));
        this.products.set(products.filter((p) => p.status === 'ACTIVE'));
        this.dialogOpen.set(true);
      },
      error: () => this.formError.set('No se pudieron cargar clientes o productos.'),
    });
  }

  addLine(): void {
    this.lineError.set(null);
    const id = this.productId();
    const qty = this.quantity();

    if (id === null) {
      this.lineError.set('Elige un producto.');
      return;
    }
    if (!Number.isInteger(qty) || qty < 1) {
      this.lineError.set('La cantidad debe ser un entero mayor o igual a 1.');
      return;
    }
    if (this.lines().some((l) => l.productId === id)) {
      this.lineError.set('Ese producto ya está en el pedido. Quítalo y agrégalo con la cantidad correcta.');
      return;
    }
    const product = this.products().find((p) => p.id === id);
    if (!product) return;

    this.lines.update((ls) => [
      ...ls,
      { productId: id, name: product.name, unitPrice: Number(product.price), quantity: qty },
    ]);
    this.productId.set(null);
    this.quantity.set(1);
  }

  removeLine(productId: number): void {
    this.lines.update((ls) => ls.filter((l) => l.productId !== productId));
  }

  submit(): void {
    this.formError.set(null);
    if (this.lines().length === 0) {
      this.formError.set('Agrega al menos un producto.');
      return;
    }
    if (this.needsTable() && this.tableId() === null) {
      this.formError.set('Elige la mesa para un pedido en mesa.');
      return;
    }

    const payload: OrderPayload = {
      clientId: this.clientId(),
      branchId: DEFAULT_BRANCH_ID,
      tableId: this.needsTable() ? this.tableId() : null,
      channel: this.channel(),
      items: this.lines().map((l) => ({ productId: l.productId, quantity: l.quantity })),
    };

    this.saving.set(true);
    this.service.create(payload).subscribe({
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

  private describe(err: HttpErrorResponse): string {
    const body = err.error;
    if (body && typeof body === 'object') {
      return Object.entries(body)
        .map(([campo, msgs]) => `${campo}: ${Array.isArray(msgs) ? msgs.join(' ') : msgs}`)
        .join(' · ');
    }
    return 'No se pudo registrar el pedido. Revisa que el backend esté corriendo.';
  }
}
