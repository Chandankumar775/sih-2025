/**
 * Client-side encryption utilities for WatchTower
 * Simulates end-to-end encryption for demonstration purposes
 */

/**
 * Encodes content to Base64 (simulation of encryption)
 */
export const encryptContent = (content: string): string => {
  try {
    return btoa(unescape(encodeURIComponent(content)));
  } catch {
    console.error("Encryption failed");
    return content;
  }
};

/**
 * Decodes Base64 content (simulation of decryption)
 */
export const decryptContent = (encrypted: string): string => {
  try {
    return decodeURIComponent(escape(atob(encrypted)));
  } catch {
    console.error("Decryption failed");
    return encrypted;
  }
};

/**
 * Generates a unique incident ID
 */
export const generateIncidentId = (): string => {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substring(2, 8);
  return `INC-${timestamp}-${random}`.toUpperCase();
};

/**
 * Hashes content for integrity verification (simplified)
 */
export const hashContent = async (content: string): Promise<string> => {
  const encoder = new TextEncoder();
  const data = encoder.encode(content);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
};
