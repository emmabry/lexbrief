// src/custom.d.ts
declare module '*.png' {
    const value: string;
    export default value;
  }
  
  declare module '*.svg?react' {
    import * as React from 'react';
  
    const ReactComponent: React.FunctionComponent<
      React.SVGProps<SVGSVGElement> & { title?: string }
    >;
  
    export default ReactComponent;
  }
  
  
  
declare module '*.css';
