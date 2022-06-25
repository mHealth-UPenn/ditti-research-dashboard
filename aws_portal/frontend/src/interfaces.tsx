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

export interface User {
  __typename: string;
  tap_permission: boolean;
  _lastChangedAt: number;
  _version: number;
  information: string;
  user_permission_id: string;
  exp_time: string;
  updatedAt: string;
  team_email: string;
  createdAt: string;
  id: string;
}
