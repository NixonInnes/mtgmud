- Found a discussion here:
  http://stackoverflow.com/questions/7943497/using-mvc-model-view-controller-in-a-client-server-architecture
- server should be it's own server.py thing
- I don't think server.py should necessarily handle any of the user interface stuff -
  i.e., I don't think it needs to store all the pages the user sees. Rather, it should
  send a signal to it's clients to say, for instance, 'show help page 1'.
- The server.py SHOULD handle all the hard lifting. This includes:
    - Storing the IP addresses and other pertinent identifying information of all the
      clients that are attached
    - Storing all user names and passwords
    - Storing each user's deck and card data
    - Storing all created tables
    - Handling user requests to create decks, add cards to decks, etc.
    - Handling administrator requests to create Tables
    - handling user requests to join/watch a game at a table
    - Handling all the mechanics of a game, i.e. shuffling a deck, dealing with the user
      drawing a card, enforcing game rules, etc.
    - I think that server.py is our Presenter, I guess...
- server.py will communicate with model.py, which will be the model in our
  model-view-presenter implementation. The job of model.py will be to:
    - manage reading/writing to the database(s)
    - provide easy-access methods for server.py - i.e. instead of having server.py do
      something like myModel.sqlRequest(mySelectStatement, myWithStatement,
      myOtherStatements), we will provide a function for each request that the server.py
      may need, so for example myModel.listUserDecks(user), myModel.listDeckCards(user,
      deckName), myModel.listAllUsers(), etc.
    - To expand on the previous bullet, this will add a good (in my opinion) level of
      abstraction to the server.py level -> server.py shouldn't have to worry about
      the specifics of the SQL request: what if we decide we don't want to use an sql
      table in the future? We don't want to have to re-write server.py. we'll just
      write model2.py and import that instead, and the access methods will be the same but
      do different things
    - ANY time that data is written to or read from our sql database (or w/e it is), it
      MUST be done through the model.py. No one else should be touching the data. This
      keeps things simple
- There will be a separate client.py that runs on any number of terminals, PCs, IP
  addresses, etc.
- The client.py will be a very 'dumb' user-interface program. It will have methods such
  as:
    - myView.showWelcome()
    - myView.showHelpScreen(1)
    - myView.clearScreen()
    - myView.mainLoop()
- The myView will not _do_ anything on it's own. Rather, it is meant to be used. Who will
  use it? In a 'classic' MVP, at least as I've used them, it'd be our presenter (so in
  this case server.py) that would hold an instance, myView, and use the methods. Since our
  Presenter is remote, though, I have a different idea....
- Have another Presenter! we'll call it presenter.py on the client side. It's job will be
  to:
    - Handle ALL communications with the server - so, it will send requests to the server
      and accept signals from the server
    - it will also use the heck out of the client.py by calling, say, myView.mainLoop()
      etc.
    - it will do any initialiations that are needed in client.py, for example setting
      Event handlers (see below)
    - it will be the main entry point into the client-side, user-experience thing of the
      program. So, 'python presenter.py' will be a way of starting the client interface
- So, to summarize, I guess we're doing a MVPP type design pattern, lol. On the
  client-side there is our Model and our server-Presenter. On the client-side there is the
  client-Presenter and the View. We COULD try to get rid of one of the presenters, but
  then we'll have client/server communication stuff happening in either the Model or the
  View, and I don't really like that idea. Alternatively, we could implement an entire MVP
  on both the client and the server side, but (for example), the View on the server side
  would essentially just bea TCP/IP manager, and ditto for the Model on the Client side.
  This may actually not be a bad approach....
- Finally, as promised, Event is described http://stackoverflow.com/a/2022629 <- there
  as:
   - So, our client (our View) will instantiate Event instances for, say, userHitsEnter =
     Event(), etc. But, the View itself won't decide what to do. The presenter will do
     things like myView.userHitsEnter.append(myView.showHelp(1)) or
     myView.userHitsEnter.append(self.doSomeThingsThenCallAViewMethod)

class Event(list):
    """Event subscription.

    A list of callable objects. Calling an instance of this will cause a
    call to each item in the list in ascending order by index.

    Example Usage:
    >>> def f(x):
    ...     print 'f(%s)' % x
    >>> def g(x):
    ...     print 'g(%s)' % x
    >>> e = Event()
    >>> e()
    >>> e.append(f)
    >>> e(123)
    f(123)
    >>> e.remove(f)
    >>> e()
    >>> e += (f, g)
    >>> e(10)
    f(10)
    g(10)
    >>> del e[0]
    >>> e(2)
    g(2)

    """
    def __call__(self, *args, **kwargs):
        for f in self:
            f(*args, **kwargs)

    def __repr__(self):
        return "Event(%s)" % list.__repr__(self)
