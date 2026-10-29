import { CurrencyPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { InputText } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { OrderDetailI } from '../../../models/business/order';
import { OrderService } from '../../../services/business/order';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

type LineRow = OrderDetailI & { orderId: number };

@Component({
  selector: 'app-lines',
  standalone: true,
  imports: [RouterLink, InputText, TableModule, Tag, CurrencyPipe],
  templateUrl: './lines.html',
  styleUrl: './lines.css',
})
export class Lines implements OnInit {
  private readonly orders = inject(OrderService);

  readonly rows = signal<LineRow[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

  readonly search = signal('');
  readonly filtered = computed(() => {
    const q = this.search().trim().toLowerCase();
    if (!q) return this.rows();
    return this.rows().filter(
      (r) => r.productName.toLowerCase().includes(q) || String(r.orderId).includes(q),
    );
  });

  readonly severity = stateSeverity;
  readonly label = stateLabel;

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.orders.getAll().subscribe({
      next: (data) => {
        this.rows.set(data.flatMap((o) => o.details.map((d) => ({ ...d, orderId: o.id }))));
        this.loading.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar las líneas. Revisa que el backend esté corriendo.');
        this.loading.set(false);
      },
    });
  }

  onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
  }
}
