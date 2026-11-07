import { HttpVerb, ResourceI } from '../../../models/security/resource';

/** Acción CRUD que se muestra como columna de la matriz. */
export type Action = 'C' | 'R' | 'U' | 'D';

/** Cada columna agrupa los verbos HTTP que cuentan para esa acción. */
export const ACTIONS: ReadonlyArray<{ key: Action; label: string; methods: HttpVerb[] }> = [
  { key: 'C', label: 'Crear', methods: ['POST'] },
  { key: 'R', label: 'Leer', methods: ['GET'] },
  { key: 'U', label: 'Actualizar', methods: ['PUT', 'PATCH'] },
  { key: 'D', label: 'Eliminar', methods: ['DELETE'] },
];

/**
 * Entidad de una ruta de la API: "api/clientes/<int:pk>/" → "clientes".
 * Las rutas sin segmento útil caen en "raiz".
 */
export function entityOf(route: string): string {
  const clean = route.replace(/^\/+/, '').replace(/^api\//, '');
  return clean.split('/')[0] || 'raiz';
}

export interface EntityRow {
  entity: string;
  /** Ids de recursos ACTIVE por acción. Lista vacía = la acción no existe para esa entidad. */
  ids: Record<Action, number[]>;
}

/** Agrupa los recursos activos por entidad. Solo cuentan los recursos ACTIVE: los inactivos no se pueden otorgar. */
export function buildEntityRows(resources: ResourceI[]): EntityRow[] {
  const byEntity = new Map<string, EntityRow>();
  for (const resource of resources) {
    if (resource.status !== 'ACTIVE') continue;
    const entity = entityOf(resource.route);
    let row = byEntity.get(entity);
    if (!row) {
      row = { entity, ids: { C: [], R: [], U: [], D: [] } };
      byEntity.set(entity, row);
    }
    for (const action of ACTIONS) {
      if (action.methods.includes(resource.method)) row.ids[action.key].push(resource.id);
    }
  }
  return [...byEntity.values()].sort((a, b) => a.entity.localeCompare(b.entity));
}

export type CellState = 'none' | 'all' | 'some' | 'off';

/** Estado de una casilla según cuántos de sus recursos están otorgados en el borrador. */
export function cellState(ids: number[], granted: ReadonlySet<number>): CellState {
  if (ids.length === 0) return 'none';
  const count = ids.filter((id) => granted.has(id)).length;
  if (count === 0) return 'off';
  return count === ids.length ? 'all' : 'some';
}

/** Devuelve un conjunto nuevo con los recursos de la casilla agregados o quitados. */
export function applyCell(granted: ReadonlySet<number>, ids: number[], on: boolean): Set<number> {
  const next = new Set(granted);
  for (const id of ids) {
    if (on) next.add(id);
    else next.delete(id);
  }
  return next;
}

/** Diferencia entre lo que hay en el servidor y el borrador. */
export function diffSets(initial: ReadonlySet<number>, draft: ReadonlySet<number>): { add: number[]; remove: number[] } {
  return {
    add: [...draft].filter((id) => !initial.has(id)),
    remove: [...initial].filter((id) => !draft.has(id)),
  };
}

/**
 * Indexa las filas de una tabla puente (role_users o resource_roles) por rol y destino.
 * Incluye filas inactivas: la base tiene un único par (rol, destino), así que hay que reactivarlas en lugar de crear otra.
 */
export function indexByRole<T extends { role: number; status: string }>(
  rows: T[],
  roleId: number,
  targetOf: (row: T) => number,
): Map<number, T> {
  const index = new Map<number, T>();
  for (const row of rows) {
    if (row.role === roleId) index.set(targetOf(row), row);
  }
  return index;
}

/** Ids de los destinos activos de un rol. */
export function activeTargets<T extends { role: number; status: string }>(
  rows: T[],
  roleId: number,
  targetOf: (row: T) => number,
): Set<number> {
  const active = new Set<number>();
  for (const row of rows) {
    if (row.role === roleId && row.status === 'ACTIVE') active.add(targetOf(row));
  }
  return active;
}
