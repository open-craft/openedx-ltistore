# Openedx LTI Store

A plugin for openedx-platform to store LTI configurations centrally. This allows course creators to add [LTI components](https://edx.readthedocs.io/projects/edx-partner-course-staff/en/latest/exercises_tools/lti_component.html) without having to enter the details like secrets, keys and URLs everytime the component block is created.

## Development

The development instructions are written with the [Open edX Devstack](https://edx.readthedocs.io/projects/open-edx-devstack/en/latest/index.html) as reference.

1. Clone the repostiory to `<devstack_root>/src/` directory
   ```sh
   cd <devstack_root>/src/
   git clone git@github.com:open-craft/openedx-ltistore.git
   ```
2. Install the plugin inside the Studio container and run migrations
   ```sh
   cd <devstack_root>/devstack/
   make studio-shell
   pip install -e /edx/src/openedx-ltistore
   python manage.py cms migrate lti_store
   exit
   ```
3. Install the plugin inside the LMS Container
   ```sh
   make lms-shell
   pip install -e /edx/src/openedx-ltistore
   exit
   ```
4. The LTI Consumer XBlock can fetch configurations to LTI Tools using `openedx-filters` mechanism. It calls the filter `org.openedx.xblock.lti_consumer.configuration.listed.v1` whenever it wants to fetch the configurations from external tools like plugins. In order for **LTI Store** to send available LTI Tools, add the following to any existing `openedx-filters` configurations for both LMS (`edx-platform/lms/envs/devstack.py` or `private.py`) and studio (`edx-platform/cms/envs/devstack.py`):
   ```py
   OPEN_EDX_FILTERS_CONFIG = {
       "org.openedx.xblock.lti_consumer.configuration.listed.v1": {
           "fail_silently": False,
           "pipeline": [
               "lti_store.pipelines.GetLtiConfigurations"
           ]
       }
   }
   ```
5. Restart the LMS & Studio for the latest config to take effect
   ```sh
   make lms-restart
   make studio-restart
   ```

Now any changes made to the source code should reflect in the application

## Adding LTI Tools to the store

1. Go to `http://localhost:18000/admin`
2. Look for `LTI_STORE` and add **External lti configurations** by clicking `+ Add` button

## Use configuration on LTI consumer XBlock

1. Go to `http://localhost:18000/admin`
2. Set the `enable_external_config_filter` waffle flag|https://github.com/openedx/xblock-lti-consumer/blob/master/lti_consumer/plugin/compat.py#L23] for your course
3. Look for `LTI_STORE` and go to **External lti configurations**
4. On the list of external LTI configurations, note down the "Filter Key" value
   of the configuration to use (Example: `lti_store:1`).
5. Copy "Filter Key" to the "External ID" field on the LTI consumer XBlock.

## Linting

The project uses [Black](https://black.readthedocs.io/en/stable/) for linting. To lint the code

```
make lint
```

## Testing

Unit tests can be run with

```
make test
```
