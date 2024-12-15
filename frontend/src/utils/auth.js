export function isTokenExpired() {
  const expiration = sessionStorage.getItem("tokenExpiration");
  const token = sessionStorage.getItem("token");

  if (!expiration || !token) return true;

  return new Date().getTime() > parseInt(expiration);
}

export function clearAuthData() {
  const authItems = [
    "token",
    "loginTime",
    "tokenExpiration",
    "userId",
    "userEmail",
    "registrationDate",
  ];
  authItems.forEach((item) => {
    localStorage.removeItem(item);
    sessionStorage.removeItem(item);
  });
}
