export type RecordStatus = 'ACTIVE' | 'INACTIVE';

export const STATUS_OPTIONS: { label: string; value: RecordStatus }[] = [
  { label: 'Activo', value: 'ACTIVE' },
  { label: 'Inactivo', value: 'INACTIVE' },
];
