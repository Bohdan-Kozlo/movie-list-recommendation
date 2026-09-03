type CatalogueMessageProps = {
  title: string
  body: string
}

export function CatalogueMessage({ title, body }: CatalogueMessageProps) {
  return (
    <div className="my-8 border-l-4 border-primary bg-card px-6 py-5">
      <h2 className="m-0 font-display text-2xl font-medium">{title}</h2>
      <p className="mt-1.5 text-muted-foreground">{body}</p>
    </div>
  )
}
