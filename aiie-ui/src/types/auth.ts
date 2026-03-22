export type TokenData = {
  sub: string;
  email: string;
};

export type AuthData = {
  tokenData: TokenData;
  accessToken: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
};
