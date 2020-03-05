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

describe('Page', () => {
  test('by alias', async () => {
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

  test('by id', async () => {
    await addResolveByIdInteraction({
      request: 19767,
      response: {
        id: 19767,
        discriminator: 'page'
      }
    })
    const response = await executeQuery(`
      {
        uuid(id: 19767) {
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
})

describe('Entity', () => {
  describe('Article', () => {
    test('by alias', async () => {
      await addResolveByAliasInteraction({
        request: {
          instance: 'de',
          path:
            '/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel'
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

    test('by id', async () => {
      await addResolveByIdInteraction({
        request: 1855,
        response: {
          id: 1855,
          discriminator: 'entity',
          type: 'article'
        }
      })
      const response = await executeQuery(`
        {
          uuid(id: 1855) {
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

async function addResolveByIdInteraction<
  T extends { discriminator: string; id: number }
>(payload: { request: number; response: T }) {
  const { request, response } = payload
  await pact.addInteraction({
    state: `${request} is an ${response.discriminator} id`,
    uponReceiving: `resolve ${request}`,
    withRequest: {
      method: 'POST',
      path: '/api/resolve-id',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        id: request
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
