import { ResourceI } from '../../../models/security/resource';
import {
  activeTargets,
  applyCell,
  buildEntityRows,
  cellState,
  diffSets,
  entityOf,
  indexByRole,
} from './rbac-matrix';

function resource(id: number, method: ResourceI['method'], route: string, status: ResourceI['status'] = 'ACTIVE'): ResourceI {
  return { id, method, route, status, createdAt: '', updatedAt: '' };
}

describe('rbac-matrix', () => {
  describe('entityOf', () => {
    it('toma el primer segmento después de api/', () => {
      expect(entityOf('api/clientes/<int:pk>/')).toBe('clientes');
      expect(entityOf('/api/recetas/(?P<pk>[^/.]+)/$')).toBe('recetas');
      expect(entityOf('api/pedidos/')).toBe('pedidos');
    });

    it('usa "raiz" cuando no hay segmento', () => {
      expect(entityOf('api/')).toBe('raiz');
    });
  });

  describe('buildEntityRows', () => {
    const resources = [
      resource(1, 'GET', 'api/clientes/'),
      resource(2, 'GET', 'api/clientes/<int:pk>/'),
      resource(3, 'POST', 'api/clientes/'),
      resource(4, 'PATCH', 'api/clientes/<int:pk>/'),
      resource(5, 'PUT', 'api/clientes/<int:pk>/'),
      resource(6, 'DELETE', 'api/clientes/<int:pk>/'),
      resource(7, 'GET', 'api/productos/', 'INACTIVE'),
      resource(8, 'POST', 'api/productos/'),
    ];

    it('agrupa por entidad y reparte cada verbo en su acción', () => {
      const rows = buildEntityRows(resources);
      const clientes = rows.find((r) => r.entity === 'clientes');
      expect(clientes?.ids.C).toEqual([3]);
      expect(clientes?.ids.R).toEqual([1, 2]);
      expect(clientes?.ids.U).toEqual([4, 5]);
      expect(clientes?.ids.D).toEqual([6]);
    });

    it('ignora recursos inactivos, así que una entidad sin activos no aparece', () => {
      const rows = buildEntityRows(resources);
      const productos = rows.find((r) => r.entity === 'productos');
      expect(productos?.ids.R).toEqual([]);
      expect(productos?.ids.C).toEqual([8]);
    });

    it('ordena las entidades alfabéticamente', () => {
      expect(buildEntityRows(resources).map((r) => r.entity)).toEqual(['clientes', 'productos']);
    });
  });

  describe('cellState', () => {
    it('distingue ninguno, todos, algunos y apagado', () => {
      expect(cellState([], new Set([1]))).toBe('none');
      expect(cellState([1, 2], new Set())).toBe('off');
      expect(cellState([1, 2], new Set([1]))).toBe('some');
      expect(cellState([1, 2], new Set([1, 2]))).toBe('all');
    });
  });

  describe('applyCell', () => {
    it('agrega y quita sin modificar el conjunto original', () => {
      const original = new Set([9]);
      const added = applyCell(original, [1, 2], true);
      expect([...added].sort()).toEqual([1, 2, 9]);
      expect([...original]).toEqual([9]);

      const removed = applyCell(added, [1], false);
      expect([...removed].sort()).toEqual([2, 9]);
    });
  });

  describe('diffSets', () => {
    it('separa altas y bajas frente al estado del servidor', () => {
      const { add, remove } = diffSets(new Set([1, 2]), new Set([2, 3]));
      expect(add).toEqual([3]);
      expect(remove).toEqual([1]);
    });
  });

  describe('indexByRole y activeTargets', () => {
    const grants = [
      { id: 10, role: 1, resource: 100, status: 'ACTIVE' },
      { id: 11, role: 1, resource: 101, status: 'INACTIVE' },
      { id: 12, role: 2, resource: 100, status: 'ACTIVE' },
    ];

    it('solo cuenta como activos los destinos ACTIVE del rol', () => {
      expect([...activeTargets(grants, 1, (g) => g.resource)]).toEqual([100]);
    });

    it('conserva también las inactivas para poder reactivarlas', () => {
      const index = indexByRole(grants, 1, (g) => g.resource);
      expect(index.get(101)?.id).toBe(11);
      expect(index.get(100)?.id).toBe(10);
    });
  });
});
