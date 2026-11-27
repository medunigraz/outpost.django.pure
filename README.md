# outpost.django.pure

Person and user feeds from CAMPUSonline for the PURE research information system.

PURE imports its people through two XML synchronisation formats:
`user-sync` for login accounts and `unified-person-sync` for person records.
This app builds both from CAMPUSonline and serves them as XML for PURE to fetch.
Each person comes with their name, titles, portrait, organisational
assignments and a link to their MEDonline business card. The app only sends
data. Nothing in PURE is read back.

Installs into the wider `outpost` project, and depends on
`outpost.django.campusonline` for employee data.

## Data and access

The app holds no data of its own. Which people go to PURE, and which of them
get a PURE login, is decided in CAMPUSonline. The first migration reads these
lists through the `campusonline` foreign server and provides them as
materialised views. They are exposed as three read-only models: `User`, `Person`
and `PersonOrganization`, all linked to their CAMPUSonline `Person`.

Every record is sent as not managed in PURE. CAMPUSonline stays the master,
and changes are made there, not in PURE. Photos come from
`Person.avatar_private`, served through campusonline's `PrivateAvatarView`,
never CAMPUSonline's public avatar URL, and only for people who allow their
photo to be shown.

The feeds contain personal data. They are available only with a bearer token
whose user may view the matching model, and in the admin to holders of the
same permissions.

## Install

```bash
pip install -e .
```

Add `outpost.django.pure` to `INSTALLED_APPS`, then:

```bash
python -m django migrate pure
```

URLs mount at `/pure/` through the usual `outpost.django.urls` discovery, the API at `/v1/pure/` through `endpoints.py`.

`outpost.django.campusonline` must be installed: all employee data comes from its `Person` model.

### Trying it out

No PURE account is needed. With the migration applied, signed in to the admin,
the three models list who would be sent. Fetch a feed with a token belonging
to a user with `pure.view_person`:

```bash
curl -H "Authorization: Bearer <token>" https://<instance>/pure/person/xml/
```

If `XML:generate` has not run, or the cache has expired, the view builds the
XML for that request. That takes a while for the full person list.

## Settings

Declared in `conf.py` with the `PURE_` prefix.

| Setting | What | Default |
|---|---|---|
| `PURE_USER_XML_CACHE_KEY` | Cache key for the generated user XML | `user` |
| `PURE_PERSON_XML_CACHE_KEY` | Cache key for the generated person XML | `person` |

The cached XML is stored with the cache backend's default timeout. If that is
shorter than the time between `XML:generate` runs, requests between expiry and
the next run build the XML on the fly.

## URLs

| Path | Purpose | Who |
|---|---|---|
| `pure:user-xml` (`user/xml/`) | PURE `user-sync` XML of all `User` rows | Bearer token with `pure.view_user` |
| `pure:person-xml` (`person/xml/`) | PURE `unified-person-sync` XML of all `Person` rows, with organisations | Bearer token with `pure.view_person` |

All three models are listed, read-only, in the Django admin.

## Tasks

| Task | What |
|---|---|
| `outpost.django.pure.tasks.XML:generate` | Build both XML documents and store them in the cache |

Schedule `XML:generate` with a periodic task in the admin, after the
materialised views refresh, so PURE reads a prebuilt document instead of
waiting for one.

## License

BSD 2-Clause, Medical University of Graz.