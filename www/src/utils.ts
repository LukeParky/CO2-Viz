export function roundToFixed(number: number, decimalPlaces = 0): string {
  const factorForIntegerRounding = 10 ** decimalPlaces
  return (Math.round(number * factorForIntegerRounding) / factorForIntegerRounding).toFixed(decimalPlaces);
}
