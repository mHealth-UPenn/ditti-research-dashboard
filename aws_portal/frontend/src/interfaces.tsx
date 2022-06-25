export interface Account {
  id: number;
  createdOn: string;
  lastLogin: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  isConfirmed: boolean;
  accessGroups: AccessGroup[];
  studies: Study[];
}

export interface App {
  id: number;
  name: string;
}

export interface AccessGroup {
  id: number;
  name: string;
  app: App;
  permissions: Permission[];
}

export interface Permission {
  id: number;
  action: string;
  resource: string;
}

export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

export interface Study {
  id: number;
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
  role: Role;
}

export interface ResponseBody {
  msg: string;
}

export interface UserDetails {
  tap_permission: boolean;
  information: string;
  user_permission_id: string;
  exp_time: string;
  team_email: string;
}

export interface User extends UserDetails {
  __typename: string;
  _lastChangedAt: number;
  _version: number;
  createdAt: string;
  updatedAt: string;
  id: string;
}

export interface TapDetails {
  time: string;
  tapUserId: string;
}

export interface Tap extends TapDetails {
  __typename: string;
  _lastChangedAt: string;
  _version: number;
  updatedAt: string;
  createdAt: string;
  id: string;
}
