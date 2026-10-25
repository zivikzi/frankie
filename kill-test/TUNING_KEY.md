# Kill test tuning key

```
4deb9efbd94bfbaf8f1087ea7148c3fb120b4941b26b2ab6ac79c76264fcff0e
```

This is the tuning key named in [KILL_TEST.md](../charter/KILL_TEST.md) section 3, committed in Week 0 as the addendum requires. It was drawn from the operating system's secure random source (Python `secrets.token_hex(32)`) on 25 Oct 2026, after the charter was frozen as tag `charter-v1`.

It generates the 30 tuning families and the throwaway practice families (numbers 1,001 and up). Looking at these families is allowed, within the limits of KILL_TEST.md section 7. It never generates a kill-run set: those keys come from Bitcoin blocks after each code freeze (KT-14).

The key is fixed from this commit on. Any change to it would show in the git history and would be reported.
