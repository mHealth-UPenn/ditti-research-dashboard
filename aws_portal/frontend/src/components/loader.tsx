import * as React from "react";

/**
 * style: the loader's style
 * msg: an optional message to display under the loader
 */
interface LoaderProps {
  style: React.CSSProperties;
  msg?: string;
}

/**
 * loading: whether the loader is not fading
 * msg: a message to display under the loader
 */
interface FullLoaderProps {
  loading: boolean;
  msg: string;
}

/**
 * loadingStyle: the style as the loader is displayed
 * fadingStyle: the style as the loader is fading
 */
interface FullLoaderState {
  loadingStyle: React.CSSProperties;
  fadingStyle: React.CSSProperties;
}

const Loader: React.FC<LoaderProps> = ({ style, msg }) => {
  return (
    <div
      id="loader"
      style={style as React.CSSProperties}
    >
      <div className="lds-ring">
        <div></div>
        <div></div>
        <div></div>
        <div></div>
      </div>
      {msg ? <span>{msg}</span> : null}
    </div>
  );
};

export const SmallLoader: React.FC = () => {
  return (
    <div className="loader-container">
      <Loader style={{}} />
    </div>
  );
};

export const FullLoader: React.FC<FullLoaderProps> = ({ loading, msg }) => {
  const loadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    position: "absolute",
    width: "100%",
    zIndex: 100,
  };

  const fadingStyle: React.CSSProperties = {
    alignItems: "center",
    backgroundColor: "white",
    display: "flex",
    flexDirection: "column",
    gap: "2rem",
    justifyContent: "center",
    height: "100%",
    opacity: 0,
    position: "absolute",
    transition: "opacity 500ms ease-in",
    width: "100%",
    pointerEvents: "none",
    zIndex: 100,
  };

  const style = loading ? loadingStyle : fadingStyle;
  return <Loader style={style} msg={msg} />;
};
