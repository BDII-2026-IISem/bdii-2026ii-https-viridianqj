import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { Button } from 'primeng/button';
import { TableModule } from 'primeng/table';
import { Tag } from 'primeng/tag';

import { ReservationI } from '../../../models/business/reservation';
import { ReservationService } from '../../../services/business/reservation';
import { stateLabel, stateSeverity } from '../../../shared/state-severity';

@Component({
  selector: 'app-getall',
  standalone: true,
  imports: [TableModule, Button, Tag, DatePipe],
  templateUrl: './getall.html',
  styleUrl: './getall.css',
})
export class Getall implements OnInit {
  private readonly service = inject(ReservationService);

  readonly items = signal<ReservationI[]>([]);
  readonly loading = signal(true);
  readonly error = signal<string | null>(null);

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
        this.error.set('No se pudo cargar reservas. Revisa que el backend esté corriendo en el puerto 8000.');
        this.loading.set(false);
      },
    });
  }
}
