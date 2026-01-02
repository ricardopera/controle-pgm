/**
 * Utility functions tests.
 */

import { describe, it, expect } from 'vitest';
import { cn, formatNumber, formatDocumentNumber, formatDate } from './utils';

describe('cn', () => {
  it('merges class names correctly', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
    expect(cn('foo', undefined, 'bar')).toBe('foo bar');
    expect(cn('foo', null, 'bar')).toBe('foo bar');
  });

  it('handles Tailwind class conflicts', () => {
    // tailwind-merge should resolve conflicts
    expect(cn('p-4', 'p-2')).toBe('p-2');
    expect(cn('text-red-500', 'text-blue-500')).toBe('text-blue-500');
  });

  it('handles conditional class names', () => {
    const isActive = false;
    expect(cn('foo', isActive && 'bar', 'baz')).toBe('foo baz');
    
    const isEnabled = true;
    expect(cn('foo', isEnabled && 'active', 'baz')).toBe('foo active baz');
  });

  it('handles empty inputs', () => {
    expect(cn()).toBe('');
    expect(cn('')).toBe('');
    expect(cn(undefined)).toBe('');
    expect(cn(null)).toBe('');
  });
});

describe('formatNumber', () => {
  it('formats numbers with leading zeros', () => {
    expect(formatNumber(1)).toBe('0001');
    expect(formatNumber(42)).toBe('0042');
    expect(formatNumber(123)).toBe('0123');
    expect(formatNumber(9999)).toBe('9999');
    expect(formatNumber(12345)).toBe('12345');
  });

  it('respects custom digit count', () => {
    expect(formatNumber(1, 6)).toBe('000001');
    expect(formatNumber(42, 2)).toBe('42');
    expect(formatNumber(5, 3)).toBe('005');
  });
});

describe('formatDocumentNumber', () => {
  it('formats full document numbers correctly', () => {
    expect(formatDocumentNumber('OF', 1, 2025)).toBe('OF 0001/2025');
    expect(formatDocumentNumber('CI', 42, 2025)).toBe('CI 0042/2025');
    expect(formatDocumentNumber('MEM', 123, 2024)).toBe('MEM 0123/2024');
  });
});

describe('formatDate', () => {
  it('formats dates in Brazilian format', () => {
    // Note: This test may need adjustment based on timezone
    const date = new Date('2025-01-15T10:30:00');
    const formatted = formatDate(date.toISOString());
    
    // Should contain the date parts
    expect(formatted).toContain('15');
    expect(formatted).toContain('01');
    expect(formatted).toContain('2025');
  });

  it('formats ISO strings correctly', () => {
    const formatted = formatDate('2025-06-20T14:30:00.000Z');
    // Should be a valid formatted date string
    expect(formatted).toBeTruthy();
    expect(typeof formatted).toBe('string');
  });
});
