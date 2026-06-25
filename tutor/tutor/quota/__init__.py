"""Hosted-course quota + spend circuit-breaker.

This whole package is dormant in local mode — local learners are never metered.
It only activates when ``TUTOR_DEPLOYMENT_MODE=hosted``.
"""
