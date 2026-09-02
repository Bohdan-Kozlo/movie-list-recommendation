import { bootstrap } from './app/bootstrap'

const rootElement = document.getElementById('root')

if (rootElement === null) {
  throw new Error('The application root is missing.')
}

bootstrap(rootElement)
