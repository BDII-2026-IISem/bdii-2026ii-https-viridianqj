import { CurrencyPipe, DatePipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { Button } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ClientI } from '../../models/business/client';
import { DeliveryI } from '../../models/business/delivery';
import { OrderI } from '../../models/business/order';
import { PaymentI } from '../../models/business/payment';
import { ClientService } from '../../services/business/client';
import { DeliveryService } from '../../services/business/delivery';
import { OrderService } from '../../services/business/order';
import { PaymentService } from '../../services/business/payment';
import { stateLabel, stateSeverity } from '../../shared/state-severity';

function sameDay(a: Date, b: Date): boolean {
  return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [RouterLink, Button, TableModule, Tag, CurrencyPipe, DatePipe],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {
  private readonly orders = inject(OrderService);
  private readonly payments = inject(PaymentService);
  private readonly deliveries = inject(DeliveryService);
  private readonly clients = inject(ClientService);

  readonly orderList = signal<OrderI[]>([]);
  readonly paymentList = signal<PaymentI[]>([]);
  readonly deliveryList = signal<DeliveryI[]>([]);
  readonly clientList = signal<ClientI[]>([]);
  readonly today = signal(new Date());
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly ordersToday = computed(() =>
    this.orderList().filter(
      (o) => o.status === 'ACTIVE' && o.orderStatus !== 'CANCELADO' && sameDay(new Date(o.orderedAt), this.today()),
    ),
  );
  readonly totalToday = computed(() => this.ordersToday().reduce((sum, o) => sum + Number(o.total), 0));
  readonly pendingPayments = computed(
    () => this.paymentList().filter((p) => p.status === 'ACTIVE' && p.paymentStatus === 'PENDIENTE').length,
  );
  readonly deliveriesOnRoad = computed(
    () => this.deliveryList().filter((d) => d.status === 'ACTIVE' && d.deliveryStatus === 'EN_CAMINO').length,
  );
  readonly activeClients = computed(() => this.clientList().filter((c) => c.status === 'ACTIVE').length);
  readonly recentOrders = computed(() => this.ordersToday().slice(0, 8));

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.today.set(new Date());
    forkJoin({
      orders: this.orders.getAll(),
      payments: this.payments.getAll(),
      deliveries: this.deliveries.getAll(),
      clients: this.clients.getAll(),
    }).subscribe({
      next: (data) => {
        this.orderList.set(data.orders);
        this.paymentList.set(data.payments);
        this.deliveryList.set(data.deliveries);
        this.clientList.set(data.clients);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudo cargar el panel. Revisa que el backend esté corriendo.');
        this.loading.set(false);
      },
    });
  }
}
