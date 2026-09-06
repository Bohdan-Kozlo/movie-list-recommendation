export const recommendationKeys = {
  personal: ['recommendations', 'personal'] as const,
  similar: (titleId: string) => ['recommendations', 'similar', titleId] as const,
}
