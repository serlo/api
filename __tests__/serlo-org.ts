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
  await addResolveByAliasInteraction({
    request: {
      instance: 'de',
      path: '/mathe'
    },
    response: {
      id: 19767,
      discriminator: 'page'
    }
  })
  const response = await executeQuery(`
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
  `)
  expect(response).toEqual({
    data: {
      uuid: {
        __typename: 'PageUuid',
        id: 19767
      }
    }
  })
})

test('Resolving the alias of an article', async () => {
  await addResolveByAliasInteraction({
    request: {
      instance: 'de',
      path: '/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel'
    },
    response: {
      id: 1855,
      discriminator: 'entity',
      type: 'article'
    }
  })
  const response = await executeQuery(`
    {
      uuid(alias: {
        instance: "de",
        path: "/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel"
      }) {
        __typename,
        ...on ArticleUuid {
          id
        }
      }
    }
  `)
  expect(response).toEqual({
    data: {
      uuid: {
        __typename: 'ArticleUuid',
        id: 1855
      }
    }
  })
})

async function addResolveByAliasInteraction<
  T extends { discriminator: string; id: number }
>(payload: { request: { instance: string; path: string }; response: T }) {
  const {
    request: { instance, path },
    response
  } = payload
  await pact.addInteraction({
    state: `${path} is alias of (${response.discriminator}, ${response.id}} in instance ${instance}`,
    uponReceiving: `resolve ${instance}.serlo.org${path}`,
    withRequest: {
      method: 'POST',
      path: '/api/resolve-alias',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        instance,
        path
      }
    },
    willRespondWith: {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: response
    }
  })
}

async function executeQuery(query: string) {
  const response = await fetch('http://localhost:8000/graphql', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query
    })
  })
  return response.json()
}

// TODO: resolve by id
// TODO: different layers for that request (e.g. number of joins?) So that the network request / sql query isn't as bad
// TODO: handle not found
