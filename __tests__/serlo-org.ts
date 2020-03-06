import { Matchers, Pact } from '@pact-foundation/pact'
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
    await addUrlAliasInteraction({
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
          instance: de,
          path: "/mathe"
        }) {
          __typename,
          ...on Page {
            id
          }
        }
      }
    `)
    expect(response).toEqual({
      data: {
        uuid: {
          __typename: 'Page',
          id: 19767
        }
      }
    })
  })

  test('by id', async () => {
    await addUuidInteraction({
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
          ...on Page {
            id
          }
        }
      }
    `)
    expect(response).toEqual({
      data: {
        uuid: {
          __typename: 'Page',
          id: 19767
        }
      }
    })
  })
})

describe('Entity', () => {
  describe('Article', () => {
    test('by alias', async () => {
      await addUrlAliasInteraction({
        request: {
          instance: 'de',
          path:
            '/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel'
        },
        response: {
          id: 1855,
          discriminator: 'entity',
          type: 'article',
          instance: 'de',
          currentRevisionId: Matchers.integer(30674),
          licenseId: Matchers.integer(1)
        }
      })
      const response = await executeQuery(`
        {
          uuid(alias: {
            instance: de,
            path: "/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel"
          }) {
            __typename,
            ...on Article {
              id
              instance
              currentRevision {
                id
              }
              license {
                id
              }
            }
          }
        }
      `)
      expect(response).toEqual({
        data: {
          uuid: {
            __typename: 'Article',
            id: 1855,
            instance: 'de',
            currentRevision: {
              id: 30674
            },
            license: {
              id: 1
            }
          }
        }
      })
    })

    test('by alias (w/ license)', async () => {
      await addUrlAliasInteraction({
        request: {
          instance: 'de',
          path:
            '/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel'
        },
        response: {
          id: 1855,
          discriminator: 'entity',
          type: 'article',
          instance: 'de',
          currentRevisionId: Matchers.integer(30674),
          licenseId: Matchers.integer(1)
        }
      })
      await pact.addInteraction({
        state: `1 is a license`,
        uponReceiving: `resolve license 1`,
        withRequest: {
          method: 'POST',
          path: '/api/license',
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 1
          }
        },
        willRespondWith: {
          status: 200,
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            id: 1,
            instance: Matchers.string('de'),
            default: Matchers.boolean(true),
            title: Matchers.string('title'),
            url: Matchers.string('url'),
            content: Matchers.string('content'),
            agreement: Matchers.string('agreement'),
            iconHref: Matchers.string('iconHref')
          }
        }
      })
      const response = await executeQuery(`
        {
          uuid(alias: {
            instance: de,
            path: "/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel"
          }) {
            __typename,
            ...on Article {
              id
              instance
              currentRevision {
                id
              }
              license {
                id
                title
              }
            }
          }
        }
      `)
      expect(response).toEqual({
        data: {
          uuid: {
            __typename: 'Article',
            id: 1855,
            instance: 'de',
            currentRevision: {
              id: 30674
            },
            license: {
              id: 1,
              title: 'title'
            }
          }
        }
      })
    })

    test('by alias (w/ currentRevision)', async () => {
      await addUrlAliasInteraction({
        request: {
          instance: 'de',
          path:
            '/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel'
        },
        response: {
          id: 1855,
          discriminator: 'entity',
          type: 'article',
          instance: 'de',
          currentRevisionId: Matchers.integer(30674),
          licenseId: Matchers.integer(1)
        }
      })
      await addUuidInteraction({
        request: 30674,
        response: {
          id: 30674,
          discriminator: 'entityRevision',
          type: 'article',
          fields: {
            title: Matchers.string('title'),
            content: Matchers.string('content'),
            changes: Matchers.string('changes')
          }
        }
      })
      const response = await executeQuery(`
        {
          uuid(alias: {
            instance: de,
            path: "/mathe/funktionen/uebersicht-aller-artikel-zu-funktionen/parabel"
          }) {
            __typename,
            ...on Article {
              id
              instance
              currentRevision {
                id
                title
                content
                changes
              }
            }
          }
        }
      `)
      expect(response).toEqual({
        data: {
          uuid: {
            __typename: 'Article',
            id: 1855,
            instance: 'de',
            currentRevision: {
              id: 30674,
              title: 'title',
              content: 'content',
              changes: 'changes'
            }
          }
        }
      })
    })

    test('by id', async () => {
      await addUuidInteraction({
        request: 1855,
        response: {
          id: 1855,
          discriminator: 'entity',
          type: 'article',
          instance: 'de',
          currentRevisionId: 30674,
          licenseId: 1
        }
      })
      const response = await executeQuery(`
        {
          uuid(id: 1855) {
            __typename,
            ...on Article {
              id
              instance
              currentRevision {
                id
              }
              license {
                id
              }
            }
          }
        }
      `)
      expect(response).toEqual({
        data: {
          uuid: {
            __typename: 'Article',
            id: 1855,
            instance: 'de',
            currentRevision: {
              id: 30674
            },
            license: {
              id: 1
            }
          }
        }
      })
    })
  })
})

test('License', async () => {
  await pact.addInteraction({
    state: `1 is a license`,
    uponReceiving: `resolve license 1`,
    withRequest: {
      method: 'POST',
      path: '/api/license',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        id: 1
      }
    },
    willRespondWith: {
      status: 200,
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        id: 1,
        instance: Matchers.string('de'),
        default: Matchers.boolean(true),
        title: Matchers.string('title'),
        url: Matchers.string('url'),
        content: Matchers.string('content'),
        agreement: Matchers.string('agreement'),
        iconHref: Matchers.string('iconHref')
      }
    }
  })
  const response = await executeQuery(`
    {
      license(id: 1) {
        id
        instance
        default
        title
        url
        content
        agreement
        iconHref
      }
    }
  `)
  expect(response).toEqual({
    data: {
      license: {
        id: 1,
        instance: 'de',
        default: true,
        title: 'title',
        url: 'url',
        content: 'content',
        agreement: 'agreement',
        iconHref: 'iconHref'
      }
    }
  })
})

describe('EntityRevision', () => {
  test('by id', async () => {
    await addUuidInteraction({
      request: 30674,
      response: {
        id: 30674,
        discriminator: 'entityRevision',
        type: 'article',
        fields: {
          title: Matchers.string('title'),
          content: Matchers.string('content'),
          changes: Matchers.string('changes')
        }
      }
    })
    const response = await executeQuery(`
        {
          uuid(id: 30674) {
            __typename,
            ...on ArticleRevision {
              id
              title
              content
              changes
            }
          }
        }
      `)
    expect(response).toEqual({
      data: {
        uuid: {
          __typename: 'ArticleRevision',
          id: 30674,
          title: 'title',
          content: 'content',
          changes: 'changes'
        }
      }
    })
  })
})

async function addUrlAliasInteraction<
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
      path: '/api/url-alias',
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

async function addUuidInteraction<
  T extends { discriminator: string; id: number }
>(payload: { request: number; response: T }) {
  const { request, response } = payload
  await pact.addInteraction({
    state: `uuid ${request} is of discriminator ${response.discriminator}`,
    uponReceiving: `resolve uuid ${request}`,
    withRequest: {
      method: 'POST',
      path: '/api/uuid',
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
