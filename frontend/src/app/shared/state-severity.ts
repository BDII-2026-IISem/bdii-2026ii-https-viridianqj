export type TagSeverity = 'success' | 'info' | 'warn' | 'danger' | 'secondary';

/** Color de la etiqueta según el estado. */
export function stateSeverity(state: string | null | undefined): TagSeverity {
  switch (state) {
    case 'ACTIVE':
    case 'LISTO':
    case 'ENTREGADO':
    case 'ENTREGADA':
    case 'PAGADO':
      return 'success';
    case 'EN_PREPARACION':
    case 'EN_CAMINO':
    case 'CONFIRMADA':
      return 'info';
    case 'PENDIENTE':
      return 'warn';
    case 'INACTIVE':
    case 'CANCELADO':
    case 'CANCELADA':
    case 'ANULADO':
      return 'danger';
    default:
      return 'secondary';
  }
}

/** Texto legible del estado. */
export function stateLabel(state: string | null | undefined): string {
  if (!state) return '—';
  if (state === 'ACTIVE') return 'Activo';
  if (state === 'INACTIVE') return 'Inactivo';
  const known: Record<string, string> = {
    EN_PREPARACION: 'En preparación',
    EN_CAMINO: 'En camino',
    DOMICILIO: 'Domicilio',
  };
  if (known[state]) return known[state];
  const text = state.replace(/_/g, ' ').toLowerCase();
  return text.charAt(0).toUpperCase() + text.slice(1);
}
