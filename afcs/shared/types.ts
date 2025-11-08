export type DatasetInfo = {
  id: string;
  name: string;
  rows: number;
  cols: number;
  numeric_cols: number;
  categorical_cols: number;
  missing_pct: number;
};
