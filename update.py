#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to update loans.png with current metrics.
Assumed to be scheduled to run multiple times a day.
"""

from image_manipulation import update_loan_stats

update_loan_stats()
