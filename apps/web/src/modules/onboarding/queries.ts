export const onboardingKeys = {
  progress: ['onboarding'] as const,
  search: (query: string, type: string) => ['onboarding', 'search', query, type] as const,
}
