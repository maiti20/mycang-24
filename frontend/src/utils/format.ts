/**
 * Formatting utility functions
 */

/**
 * Format date to YYYY-MM-DD
 */
export function formatDate(dateStr: string | Date): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).replace(/\//g, '-')
}

/**
 * Format time to HH:mm
 */
export function formatTime(dateStr: string | Date): string {
  const date = new Date(dateStr)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  })
}

/**
 * Format datetime to YYYY-MM-DD HH:mm
 */
export function formatDateTime(dateStr: string | Date): string {
  return `${formatDate(dateStr)} ${formatTime(dateStr)}`
}

/**
 * Format relative time (e.g., "2 hours ago", "yesterday")
 */
export function formatRelativeTime(dateStr: string | Date): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffMins < 1) return '刚刚'
  if (diffMins < 60) return `${diffMins}分钟前`
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays === 1) return '昨天'
  if (diffDays < 7) return `${diffDays}天前`
  if (diffDays < 30) return `${Math.floor(diffDays / 7)}周前`
  return formatDate(dateStr)
}

/**
 * Format number with thousand separator
 */
export function formatNumber(num: number, decimals: number = 0): string {
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

/**
 * Format calories
 */
export function formatCalories(cal: number): string {
  return `${formatNumber(Math.round(cal))} 卡`
}

/**
 * Format duration in minutes to readable string
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) return `${minutes}分钟`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  if (mins === 0) return `${hours}小时`
  return `${hours}小时${mins}分钟`
}

/**
 * Format weight (kg)
 */
export function formatWeight(weight: number): string {
  return `${weight.toFixed(1)} kg`
}

/**
 * Format height (cm)
 */
export function formatHeight(height: number): string {
  return `${Math.round(height)} cm`
}

/**
 * Format percentage
 */
export function formatPercent(value: number, total: number): string {
  if (total === 0) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

/**
 * Format BMI
 */
export function formatBMI(height: number, weight: number): { value: number; status: string; color: string } {
  const heightM = height / 100
  const bmi = weight / (heightM * heightM)

  let status: string
  let color: string

  if (bmi < 18.5) {
    status = '偏瘦'
    color = 'info'
  } else if (bmi < 24) {
    status = '正常'
    color = 'success'
  } else if (bmi < 28) {
    status = '偏胖'
    color = 'warning'
  } else {
    status = '肥胖'
    color = 'danger'
  }

  return { value: Math.round(bmi * 10) / 10, status, color }
}
