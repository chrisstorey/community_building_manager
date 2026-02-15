# Community Building Manager
## overall the service should comply to 12 factor application paradigms
## the service is to be written in Python and fastapi.
## database should be Fastapi, but abstracted so that it can use postgres at a later stage  
## UI components are to use bootstrap5
## always write tests

# Brand Identity: Community Building Manager

## Visual Personality
- **Tone:** Reliable, organized, civic-minded, and sturdy.
- **Accessibility Standard:** WCAG 2.1 AA minimum.

## Color Specifications
- **Primary (Brand):** #1A365D (Deep Navy) - Use for authority and structure.
- **Secondary (Action):** #D97706 (Amber) - Use for "Requires Attention" or main CTAs.
- **Success/Safety:** #059669 (Emerald) - Use for "Maintained" or "Asset Functional".
- **Neutral/Background:** #F8FAFC (Cool Grey) - Use for page backgrounds to keep the UI "airy".
- **Text:** #1E293B (Slate) - Use for all body copy to ensure high legibility.

## UI Principles
- **Radius:** Use a 6px or 8px border-radius on buttons and cards for a modern but friendly feel.
- **Hierarchy:** Headers must always use Foundation Blue. Actionable items must use Safety Amber.
- **Iconography:** Use bold, thick-stroked icons (2px minimum) to represent assets like boilers, roofs, and fire extinguishers.

# Service description

Community Building manager is a service that allows those in management roles to manage and audit their community buildings and activities.  The service will help a building manager know what they need to consider; and then manage those areas over time.  It will remind users when actions are needed and collect the results/manage progress. 

1. Users should login and are allocated either, admin, manager, or viewer roles.
2. A user is associated with an organisation
3. organisations have locations
4. organisations can have parent organisations
5. an organisation has key details such as Name, Address and key contacts - there can be more than one key contact.
6. an organisation has a dashboard that shows the number of actions outstanding and those that are due in the next month.
7. A location has an address and any number of asset types can be allocated to it.  The key types of location are - scout HQ; scout campsite; church; church hall; community building; scout activity centre.
8. each building type has a series of areas used as a template.  Templates are  written in markdown and have two levels: area and item.
9. when a location is added, the user can add an instance of an asset type.  The markdown template is used to create a series of work items listed in work areas.
10. work areas have a statement and overall relevant, not relevant state, and a number of items listed.
11. each work item has a statement, a description, and a series of updates, each update has a narrative i.e. what was done or is needed, which user did it and when.  a review date is also present.  
