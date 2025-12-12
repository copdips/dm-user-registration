# Building a user registration API

- [Building a user registration API](#building-a-user-registration-api)
  - [Context](#context)
  - [Specifications](#specifications)
  - [What do we expect?](#what-do-we-expect)
  - [Layout](#layout)
  - [Usage](#usage)

## Context

Handles user registrations. To do so, user creates an account and we send a code by email to verify the account.

As a core API developer, you are responsible for building this feature and expose it through API.

## Specifications

You have to manage a user registration and his activation.

The API must support the following use cases:

- Create a user with an email and a password.
- Send an email to the user with a 4 digits code.
- Activate this account with the 4 digits code received. For this step, we consider a `BASIC AUTH` is enough to check if he is the right user.
- The user has only one minute to use this code. After that, an error should be raised.

Design and build this API. You are completely free to propose the architecture you want.

## What do we expect?

- Python language is required.

- We expect to have a level of code quality which could go to production.
- Using frameworks is allowed only for routing, dependency injection, event dispatcher, db connection. Don't use magic (for example SQLAlchemy, even without its ORM)! We want to see **your** implementation.
- Use the DBMS you want (except SQLite).
- Consider the SMTP server as a third party service offering an HTTP API. You can mock the call, use a local SMTP server running in a container, or simply print the 4 digits in console. But do not forget in your implementation that **it is a third party service**.
- Your code should be tested.
- Your application has to run within a docker containers.
- You can use AI to help you, but in a smart way. However, please make iterative commits as we analyze them to understand your development reasoning (not all the code in 1 or 2 commits).
- You should provide us the link to GitHub.
- You should provide us the instructions to run your code and your tests. We should not install anything except docker/docker-compose to run you project.
- You should provide us an architecture schema.

## Layout

```plaintext
├── scripts
│   └── init_db.sql
├── src
│   └── app
│       ├── application
│       │   ├── dto
│       │   │   └── user_dto.py
│       │   ├── exceptions.py
│       │   ├── ports
│       │   │   ├── code_store.py
│       │   │   ├── event_publisher.py
│       │   │   └── user_repository.py
│       │   └── use_cases
│       │       ├── activate_user.py
│       │       ├── register_user.py
│       │       └── resend_code.py
│       ├── config.py
│       ├── container.py
│       ├── domain
│       │   ├── entities
│       │   │   └── user.py
│       │   ├── events
│       │   │   ├── base.py
│       │   │   └── user_events.py
│       │   ├── exceptions.py
│       │   └── value_objects
│       │       ├── email.py
│       │       ├── password.py
│       │       ├── user_id.py
│       │       └── verification_code.py
│       ├── infrastructure
│       │   ├── code_store
│       │   │   ├── memory_code_store.py
│       │   │   └── redis_code_store.py
│       │   ├── database
│       │   │   ├── mappers
│       │   │   │   └── user_mapper.py
│       │   │   ├── models
│       │   │   │   └── user_model.py
│       │   │   └── repositories
│       │   │       └── postgres_user_repository.py
│       │   └── event_publisher
│       │       └── console_event_publisher.py
│       ├── main.py
│       └── presentation
│           ├── dependencies.py
│           ├── exception_handlers.py
│           ├── routers
│           │   └── v1
│           │       └── users.py
│           └── schemas
│               └── users.py
├── tests
│   ├── fakes
│   │   ├── fake_code_store.py
│   │   ├── fake_event_publisher.py
│   │   └── fake_user_repository.py
│   ├── integration
│   │   ├── conftest.py
│   │   └── test_v1_users.py
│   └── unit
│       ├── application
│       │   └── use_cases
│       │       ├── conftest.py
│       │       ├── test_activate_user.py
│       │       ├── test_register_user.py
│       │       └── test_resend_code.py
│       └── domain
│           ├── entities
│           │   ├── conftest.py
│           │   └── test_user.py
│           └── value_objects
│               ├── test_email.py
│               ├── test_password.py
│               ├── test_user_id.py
│               └── test_verification_code.py
```

## Usage

1. Install: `make install`
2. Run unit test (does not require Postgres and Redis running): `make test-unit`
3. Start Postgres and Redis: `make start-docker-compose`, optional step, will be automatically started when running integration tests or application.
4. Run integration test: `make test-integration`
5. Run full tests: `make test`
6. Run application: `make run`, and API will be available at `http://localhost:8000/docs`
7. Stop Postgres and Redis: `make stop-docker-compose`

> [!NOTE]
>
> - Current implementation for event publisher just prints to console, but it would be nice to use RabbitMQ, but need more time to implement it.
> - SQL operations are not using transactions for simplicity, will be added later.
> - request and response are not logged, but can be added later with middleware.
> - logging will be added later.
> - x-correlation-id header can be added later for tracing.
