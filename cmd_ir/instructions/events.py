"""Events"""

from ._core import (PreambleOnlyInsn, ConstructorInsn, Insn, SingleCommandInsn,
                    VoidApplicationInsn)
from ..core_types import (VirtualString,
                          EventRef,
                          Selector,
                          SelectorType,
                          )
from ..core import IRFunction, VisibleFunction
import commands as c

class CreateEvent(PreambleOnlyInsn, ConstructorInsn):
    """Creates a new event object."""

    args = [VirtualString]
    argnames = 'event_name'
    argdocs = ["The event name"]
    rettype = EventRef
    top_preamble_only = True
    insn_name = 'event'

    def construct(self):
        return EventRef(str(self.event_name))

class AddEventCondition(PreambleOnlyInsn, Insn):
    """Add a condition to an event that must be true for the event handler
    to be invoked."""

    is_virtual = True

    args = [EventRef, VirtualString, VirtualString]
    argnames = 'event path value'
    argdocs = ["Event to add the condition to", "JSON path in the advancement",
               "Value that must match"]
    top_preamble_only = True
    insn_name = 'add_event_condition'

    def apply(self, out, top):
        # TODO put in activate
        self.event.add_condition(tuple(str(self.path).split('.')),
                                 str(self.value))

class EventHandler(PreambleOnlyInsn, Insn):
    """Add an event handler to the given event specification."""

    args = [IRFunction, EventRef]
    argnames = 'handler event'
    argdocs = ["Event handler", "Event"]
    top_preamble_only = True
    insn_name = 'event_handler'

    def activate(self, seq):
        if self.event.name not in ['minecraft:tick', 'minecraft:load']:
            self.handler.add_advancement_revoke(self.event)

    def declare(self):
        self.handler.usage()

    def apply(self, out, top):
        out.write_event_handler(self.handler, self.event)

class RevokeEventAdvancement(SingleCommandInsn):
    """(Internal) Revokes an advancement to allow an event to re-fire."""

    args = [IRFunction]
    argnames = 'func'
    argdocs = ["Handler"]
    insn_name = 'revoke_event_adv'

    def get_cmd(self):
        # Advancement name = handler func name
        return c.Advancement('revoke', Selector(SelectorType.SENDER) \
                             .as_resolve(),
                           'only', c.AdvancementRef(self.func.global_name))

class ExternInsn(PreambleOnlyInsn, VoidApplicationInsn):
    """Marks the function as externally visible. The function will not
    be removed during optimization."""

    args = []
    argnames = ''
    func_preamble_only = True
    insn_name = 'extern'

    def activate(self, seq):
        seq.holder.set_extern(True)

class PureInsn(PreambleOnlyInsn, VoidApplicationInsn):
    """Marks the function as a pure function (i.e. no side-effects). No checks
    are done to ensure it is side-effect free, allowing for functions with
    irrelevant side-effects (e.g. caching) to be marked as pure."""

    args = []
    argnames = ''
    func_preamble_only = True
    insn_name = 'pure_func'

    def activate(self, seq):
        seq.holder.set_pure()

class SetupInsn(PreambleOnlyInsn, Insn):
    """Tags a function as being part of the setup phase. It is called whenever
    the datapack is reloaded."""

    args = [VisibleFunction]
    argnames = 'func'
    argdocs = ["The setup function"]
    top_preamble_only = True
    insn_name = 'setupfn'

    def declare(self):
        self.func.usage()

    def apply(self, out, top):
        out.write_setup_function(self.func)
