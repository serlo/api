import { Pact } from '@pact-foundation/pact'
import fetch from 'node-fetch'
import * as path from 'path'
import rimraf from 'rimraf'
import * as util from 'util'

const rm = util.promisify(rimraf)

const root = path.join(__dirname, '..')
const pactDir = path.join(root, 'pacts')

const pact = new Pact({
  consumer: 'api.serlo.org',
  provider: 'serlo.org',
  port: 9009,
  dir: pactDir
})

beforeAll(async () => {
  await rm(pactDir)
  await pact.setup()
})

afterEach(async () => {
  await pact.verify()
})

afterAll(async () => {
  await pact.finalize()
})

test('Resolving the alias of a page', async () => {
  await pact.addInteraction({
    state: '/mathe is alias of /page/view/19767 in instance de',
    uponReceiving: 'resolve de.serlo.org/mathe',
    withRequest: {
      method: 'POST',
      path: '/api/resolve-alias',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        instance: 'de',
        path: '/mathe'
      }
    },
    willRespondWith: {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        id: 19767,
        type: 'page'
      }
    }
  })
  const response = await fetch('http://localhost:8000/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: `
        {
          uuid(alias: {
            instance: "de",
            path: "/mathe"
          }) {
            __typename,
            ...on PageUuid {
              id
            }
          }
        }
      `
    })
  })
  expect(await response.json()).toEqual({
    data: {
      uuid: {
        __typename: 'PageUuid',
        id: 19767
      }
    }
  })
})

// TODO: resolve by id
// TODO: different layers for that request (e.g. number of joins?) So that the network request / sql query isn't as bad
// TODO: handle not found
