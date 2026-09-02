import { cva, type VariantProps } from 'class-variance-authority'
import { Slot } from 'radix-ui'
import { type ButtonHTMLAttributes, forwardRef } from 'react'

import { cn } from '../lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap border border-primary px-4 py-3 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/85',
        outline: 'bg-transparent text-primary hover:bg-primary hover:text-primary-foreground',
        ghost: 'border-transparent bg-transparent text-muted-foreground hover:border-current hover:text-foreground',
      },
      size: {
        default: 'h-11',
        compact: 'h-8 px-2 py-1 text-xs',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  },
)

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants> & { asChild?: boolean }

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { asChild, className, variant, size, ...props },
  ref,
) {
  const Component = asChild ? Slot.Root : 'button'
  return <Component className={cn(buttonVariants({ variant, size }), className)} ref={ref} {...props} />
})
