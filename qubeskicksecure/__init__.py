# -*- encoding: utf-8 -*-
#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2018 Marek Marczykowski-Górecki
#                               <marmarek@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

"""qubes-core-admin extension for handling Kicksecure related settings"""

import qubes.ext
import qubes.vm.templatevm


class QubesKicksecureExtension(qubes.ext.Extension):
    """qubes-core-admin extension for handling Kicksecure related settings"""

    def apply_tags(self, vm):
        """Apply the appropriate tags to Kicksecure VMs."""
        if not isinstance(vm, qubes.vm.LocalVM):
            return

        if vm.features.check_with_template(
            "whonix-gw", None
        ) or vm.features.check_with_template("whonix-ws", None):
            return

        if vm.features.check_with_template("kicksecure", None):
            vm.tags.add("sdwdate-gui-client")
        else:
            vm.tags.discard("sdwdate-gui-client")

    @qubes.ext.handler("domain-add", system=True)
    def on_domain_add(self, app, _event, vm, **_kwargs):
        """Handle new AppVM created on kicksecure template and adjust its
        default settings
        """
        # pylint: disable=unused-argument
        self.apply_tags(vm)

    @qubes.ext.handler("features-request")
    def on_features_request(self, vm, _event, untrusted_features):
        """Handle kicksecure template advertising itself"""
        # Allow VM to advertise itself as kicksecure. But do not allow to drop
        #  that info on its own
        if not isinstance(vm, qubes.vm.templatevm.TemplateVM):
            return
        if "kicksecure" in untrusted_features:
            vm.features["kicksecure"] = True

    @qubes.ext.handler("domain-load")
    def on_domain_load(self, vm, _event):
        """Retroactively add tags to kicksecure."""
        self.apply_tags(vm)

    @qubes.ext.handler(
        "property-set:template",
        "property-reset:active_template",
    )
    def on_property_set_template(
        self, vm, event, name, newvalue=None, oldvalue=None
    ):
        """Add tags to AppVMs that become based upon Kicksecure."""
        # pylint: disable=too-many-positional-arguments,unused-argument
        self.apply_tags(vm)
