export function isTokenExpired() {
  const expiration = sessionStorage.getItem("tokenExpiration");
  const token = sessionStorage.getItem("token");

  if (!expiration || !token) return true;

  try {
    // 嘗試解析 expiration 為數字
    const expirationTime = parseInt(expiration);
    if (isNaN(expirationTime)) return true;
    
    // 檢查是否過期
    return new Date().getTime() > expirationTime;
  } catch (e) {
    console.error("Error checking token expiration:", e);
    return true; // 如果有錯誤，視為過期
  }
}

export function clearAuthData() {
  const authItems = [
    "token",
    "loginTime",
    "tokenExpiration",
    "userId",
    "userEmail",
    "registrationDate",
    "guestmode"
  ];
  authItems.forEach((item) => {
    localStorage.removeItem(item);
    sessionStorage.removeItem(item);
  });
}

export function isGuestMode() {
  return localStorage.getItem("guestmode");
}

export function isAuthenticated() {
  return !!sessionStorage.getItem("token") && !isTokenExpired(); // !!會將值轉換為布林值
}