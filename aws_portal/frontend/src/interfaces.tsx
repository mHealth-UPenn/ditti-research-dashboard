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
  tapPermission: boolean;
  information: string;
  userPermissionId: string;
  expTime: string;
  teamEmail: string;
  createdAt: string;
}

export interface User {
  tap_permission: boolean;
  information: string;
  user_permission_id: string;
  exp_time: string;
  team_email: string;
  createdAt: string;
  __typename: string;
  _lastChangedAt: number;
  _version: number;
  updatedAt: string;
  id: string;
}

export interface TapDetails {
  dittiId: string;
  time: Date;
}

export interface Tap {
  dittiId: string;
  time: string;
}

export interface ViewProps {
  flashMessage: (msg: React.ReactElement, type: string) => void;
  goBack: () => void;
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}
