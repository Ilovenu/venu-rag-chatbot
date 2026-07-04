export interface ApiEnvelope<T> {
  responseCode: number;
  message?: string;
  products?: T;
  brands?: T;
  user?: T;
}
