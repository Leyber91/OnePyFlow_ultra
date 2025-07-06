import logging
import json
import requests

# Configure logging
logger = logging.getLogger(__name__)


def send_graphql_request(graphql_endpoint, id_token, site_name):
    """
    Sends a GraphQL query to the DockFlow API to retrieve workcell data.
    """
    logger.info("Sending GraphQL request to DockFlow API.")
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json",
    }
    graphql_query = """
    query getSite($siteName: String!, $outboundArcName: String) {
      site(siteName: $siteName, outboundArcName: $outboundArcName) {
        name
        workcells {
          id {
            name
            type
            siteName
            __typename
          }
          workState {
            capacity
            utilization
            backlog
            rate {
              capacity
              aggregateRate
              previous {
                interval
                rate
                __typename
              }
              projected {
                interval
                rate
                __typename
              }
              __typename
            }
            __typename
          }
          statusEvents {
            level
            event
            details
            value
            __typename
          }
          areas {
            name
            type
            workState {
              capacity
              utilization
              backlog
              rate {
                capacity
                aggregateRate
                previous {
                  interval
                  rate
                  __typename
                }
                projected {
                  interval
                  rate
                  __typename
                }
                __typename
              }
              __typename
            }
            sspContainerId
            statusEvents {
              level
              event
              details
              value
              __typename
            }
            outboundArcName
            attributes {
              key
              value
              __typename
            }
            __typename
          }
          outboundArcs {
            name
            sspSortkey
            crsDestination
            workState {
              capacity
              utilization
              backlog
              rate {
                capacity
                aggregateRate
                previous {
                  interval
                  rate
                  __typename
                }
                projected {
                  interval
                  rate
                  __typename
                }
                __typename
              }
              __typename
            }
            statusEvents {
              level
              event
              details
              value
              __typename
            }
            __typename
          }
          parents {
            id {
              name
              type
              siteName
              __typename
            }
            propagation
            __typename
          }
          children {
            id {
              name
              type
              siteName
              __typename
            }
            propagation
            __typename
          }
          alias
          tags {
            key
            value
            __typename
          }
          __typename
        }
        outboundArcs {
          name
          sspSortkey
          crsDestination
          workState {
            capacity
            utilization
            backlog
            rate {
              capacity
              aggregateRate
              previous {
                interval
                rate
                __typename
              }
              projected {
                interval
                rate
                __typename
              }
              __typename
            }
            __typename
          }
          statusEvents {
            level
            __typename
          }
          workcells {
            id {
              name
              type
              siteName
              __typename
            }
            alias
            __typename
          }
          __typename
        }
        siteConfig {
          siteName
          siteType {
            type
            version
            availableTags {
              key
              value
              __typename
            }
            __typename
          }
          aimStream
          lastUpdatedBy
          __typename
        }
        __typename
      }
    }
    """
    payload = {
        "operationName": "getSite",
        "variables": {"siteName": site_name},
        "query": graphql_query,
    }

    try:
        response = requests.post(graphql_endpoint, headers=headers, json=payload, verify=False)
        logger.info(f"GraphQL request status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        logger.debug(f"GraphQL response data: {json.dumps(data, indent=2)}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending GraphQL request: {e}")
        raise
