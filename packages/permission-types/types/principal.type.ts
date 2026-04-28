import { UserLevel } from '../enums/user-level.enum';
import { UserType } from '../enums/user-type.enum';
import { Product } from '../enums/product.enum';

export type Principal = {
  userId: string;
  userLevel: UserLevel;
  userType: UserType;
  retailerId?: string;
  products?: Product[];
};
