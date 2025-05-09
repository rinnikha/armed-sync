declare module 'react-icons/fi' {
  import { ComponentType } from 'react';

  interface IconBaseProps {
    size?: string | number;
    color?: string;
    className?: string;
  }

  type IconType = ComponentType<IconBaseProps>;

  export const FiMenu: IconType;
  export const FiLayout: IconType;
  export const FiShoppingCart: IconType;
  export const FiPackage: IconType;
  export const FiRefreshCw: IconType;
  export const FiBarChart2: IconType;
  export const FiDollarSign: IconType;
  export const FiLogOut: IconType;
  export const FiPlus: IconType;
  export const FiEdit: IconType;
  export const FiTrash2: IconType;
  export const FiEye: IconType;
  export const FiDownload: IconType;
  export const FiTrendingUp: IconType;
  export const FiTrendingDown: IconType;
  export const FiAlertTriangle: IconType;
  export const FiAlertCircle: IconType;
  export const FiInfo: IconType;
  export const FiCheckCircle: IconType;
} 