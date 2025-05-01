/**
 * Props for the Loader component.
 * @property style - The style of the loader.
 * @property msg - An optional message to display under the loader.
 */
export interface LoaderProps {
  style: React.CSSProperties;
  msg?: string;
}

/**
 * Props for the FullLoader component.
 * @property loading - Whether the loader is not fading.
 * @property msg - A message to display under the loader.
 */
export interface FullLoaderProps {
  loading: boolean;
  msg: string;
}
