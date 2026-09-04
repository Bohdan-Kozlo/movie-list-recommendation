import { Link, NavLink } from 'react-router'

import { AccountMenu } from '../auth/AccountMenu'
import { cn } from '../../shared/lib/utils'

type SiteHeaderProps = {
  className?: string
  onBrandClick?: () => void
}

const navigation = [
  { to: '/catalogue', label: 'Catalogue' },
  { to: '/recommendations', label: 'Recommendations' },
  { to: '/library/watchlist', label: 'Library' },
]

export function SiteHeader({ className, onBrandClick }: SiteHeaderProps) {
  return (
    <header className={cn('flex min-h-21 items-center gap-5 border-b border-border/80 py-3 max-md:flex-wrap', className)}>
      <Link
        className="group flex shrink-0 items-center gap-2 font-display text-xl font-bold tracking-[-.055em]"
        onClick={onBrandClick}
        to="/catalogue"
      >
        <span className="grid size-7 place-items-center bg-primary font-mono text-[10px] tracking-normal text-primary-foreground">R</span>
        REEL <span className="text-primary">/</span> INDEX
      </Link>
      <nav aria-label="Main navigation" className="order-3 flex w-full gap-1 overflow-x-auto border-t border-border/50 pt-2 text-sm md:order-none md:w-auto md:border-0 md:pt-0">
        {navigation.map((item) => (
          <NavLink
            className={({ isActive }) => cn(
              'shrink-0 border-b-2 px-3 py-2 font-mono text-xs uppercase tracking-[.07em] transition-colors',
              isActive ? 'border-primary text-primary' : 'border-transparent text-muted-foreground hover:text-foreground',
            )}
            key={item.to}
            to={item.to}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="ml-auto"><AccountMenu /></div>
    </header>
  )
}
