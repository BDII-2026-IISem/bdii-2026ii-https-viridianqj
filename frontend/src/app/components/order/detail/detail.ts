import { CurrencyPipe, DatePipe } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Button } from 'primeng/button';
import { Tag } from 'primeng/tag';

import { OrderI } from '../../../models/business/order';
import { OrderService } from '../../../services/business/order';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

@Component({
  selector: 'app-detail',
  standalone: true,
  imports: [RouterLink, Button, Tag, CurrencyPipe, DatePipe],
  templateUrl: './detail.html',
  styleUrl: './detail.css',
})
export class Detail implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly service = inject(OrderService);
  private id = 0;

  readonly order = signal<OrderI | null>(null);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);
  readonly voiding = signal(false);

  readonly isVoided = computed(() => {
    const o = this.order();
    return !o || o.orderStatus === 'CANCELADO' || o.status === 'INACTIVE';
  });

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  ngOnInit(): void {
    this.id = Number(this.route.snapshot.paramMap.get('id'));
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.service.getById(this.id).subscribe({
      next: (o) => {
        this.order.set(o);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se encontró el pedido o el backend no responde.');
        this.loading.set(false);
      },
    });
  }

  anular(): void {
    const o = this.order();
    if (!o) return;
    if (!confirm(`¿Anular el pedido #${o.id}? Quedará cancelado y sus líneas se desactivarán.`)) return;

    this.voiding.set(true);
    this.service.void(o.id).subscribe({
      next: () => {
        this.voiding.set(false);
        this.load();
      },
      error: (err: HttpErrorResponse) => {
        this.voiding.set(false);
        this.error.set(`No se pudo anular el pedido: ${JSON.stringify(err.error)}`);
      },
    });
  }
}
