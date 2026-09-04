import type { KeyboardEvent, MouseEvent } from 'react'

type StarRatingProps = {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
  label: string
}

const stars = [1, 2, 3, 4, 5]

export function StarRating({ value, onChange, disabled = false, label }: StarRatingProps) {
  function choose(event: MouseEvent<HTMLButtonElement>, star: number) {
    const bounds = event.currentTarget.getBoundingClientRect()
    onChange(event.clientX < bounds.left + bounds.width / 2 ? star - 0.5 : star)
  }

  function adjust(event: KeyboardEvent<HTMLButtonElement>, change: number) {
    if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return
    event.preventDefault()
    onChange(Math.min(5, Math.max(0.5, value + change)))
  }

  return (
    <div className="flex items-center gap-1" role="group" aria-label={label}>
      {stars.map((star) => {
        const fill = value >= star ? 100 : value >= star - 0.5 ? 50 : 0
        return (
          <button
            aria-label={`Set rating to ${star}. Click the left half for ${star - 0.5}.`}
            className="grid size-11 place-items-center text-4xl leading-none text-[#597083] transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:cursor-not-allowed disabled:opacity-50"
            disabled={disabled}
            key={star}
            onClick={(event) => choose(event, star)}
            onKeyDown={(event) => adjust(event, event.key === 'ArrowLeft' ? -0.5 : 0.5)}
            type="button"
          >
            <span
              aria-hidden="true"
              style={{
                backgroundImage: `linear-gradient(90deg, #e8a657 ${fill}%, currentColor ${fill}%)`,
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              ★
            </span>
          </button>
        )
      })}
      <output className="ml-2 font-mono text-sm text-muted-foreground" aria-live="polite">
        {value.toFixed(1)} / 5
      </output>
    </div>
  )
}
