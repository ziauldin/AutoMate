import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function showNotification(message: string, type: "info" | "success" | "error" | "warning" = "info") {
  // Create notification element
  const notification = document.createElement("div")
  notification.className = `notification ${type}`

  // Set icon based on type
  let icon = "info-circle"
  if (type === "success") icon = "check-circle"
  if (type === "error") icon = "exclamation-circle"
  if (type === "warning") icon = "exclamation-triangle"

  notification.innerHTML = `
    <i class="fas fa-${icon}"></i>
    <span>${message}</span>
  `

  // Add to document
  document.body.appendChild(notification)

  // Animate in
  setTimeout(() => {
    notification.classList.add("show")
  }, 10)

  // Remove after delay
  setTimeout(() => {
    notification.classList.remove("show")
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 300)
  }, 3000)
}
