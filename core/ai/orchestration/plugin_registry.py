from __future__ import annotations

from core.ai.orchestration.action_plugins.endpoint_isolation import (
    EndpointIsolationPlugin,
)

from core.ai.orchestration.action_plugins.mailbox_quarantine import (
    MailboxQuarantinePlugin,
)

from core.ai.orchestration.action_plugins.evidence_sealing import (
    EvidenceSealingPlugin,
)
from core.ai.orchestration.action_plugins.session_revocation import (
    SessionRevocationPlugin,
)

from core.ai.orchestration.action_plugins.user_disablement import (
    UserDisablementPlugin,
)

class PluginRegistry:

    def __init__(self, storage=None):

        self.plugins = {
            "endpoint_isolation":
                EndpointIsolationPlugin(storage),

            "mailbox_quarantine":
                MailboxQuarantinePlugin(storage),

            "evidence_sealing":
                EvidenceSealingPlugin(storage),

            "session_revocation": SessionRevocationPlugin(storage),
            "user_disablement": UserDisablementPlugin(storage),
        }

    def get(self, action: str):

        return self.plugins.get(action)