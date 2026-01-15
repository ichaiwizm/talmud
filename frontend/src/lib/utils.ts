import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import type { NameType } from '../api/types';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const NAME_TYPE_LABELS: Record<NameType, string> = {
  person: 'Person',
  deity: 'Deity',
  place: 'Place',
  people_group: 'People',
  angel: 'Angel',
  unknown: 'Unknown',
};

export const NAME_TYPE_COLORS: Record<NameType, string> = {
  person: 'bg-torah-blue',
  deity: 'bg-gold-700',
  place: 'bg-torah-green',
  people_group: 'bg-torah-purple',
  angel: 'bg-[#5e3a6e]',
  unknown: 'bg-ink-lighter',
};

export const TORAH_BOOKS = [
  { name: 'Genesis', hebrew: 'בראשית' },
  { name: 'Exodus', hebrew: 'שמות' },
  { name: 'Leviticus', hebrew: 'ויקרא' },
  { name: 'Numbers', hebrew: 'במדבר' },
  { name: 'Deuteronomy', hebrew: 'דברים' },
];

export const GEMATRIA_METHODS = [
  { value: 'standard', label: 'Standard', description: 'Traditional values (א=1, ב=2...)' },
  { value: 'katan', label: 'Katan', description: 'Reduced to 1-9' },
  { value: 'ordinal', label: 'Ordinal', description: 'Position in alphabet (1-22)' },
  { value: 'atbash', label: 'Atbash', description: 'Cipher substitution' },
] as const;

export function formatNumber(num: number): string {
  return new Intl.NumberFormat().format(num);
}

export function parseVerseRef(ref: string): { book: string; chapter: number; verse: number } | null {
  const match = ref.match(/^(.+)\s+(\d+):(\d+)$/);
  if (!match) return null;
  return {
    book: match[1],
    chapter: parseInt(match[2], 10),
    verse: parseInt(match[3], 10),
  };
}
