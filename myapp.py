from myapp import app, db
from myapp.models import User, UserLogging, PrivateRoutes
from myapp import PRIVATE_ROUTES
import sys
import argparse


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

def change_active_status(emails, change):
    emails=",".join(emails)
    emails=emails.replace(" ", "")
    for e in emails.split(","):
        user=User.query.filter_by(email=e).first()
        if not user:
            print(e, "could not be found!" )
            sys.stdout.flush()
        else:
            user.active=change
            db.session.add(user)
            db.session.commit()
            print(f'{e}: user.active={user.active}')
            sys.stdout.flush()

def change_admin(emails, change):
    emails=",".join(emails)
    emails=emails.replace(" ", "")
    for e in emails.split(","):
        user=User.query.filter_by(email=e).first()
        if not user:
            print(e, "could not be found!" )
            sys.stdout.flush()
        else:
            user.administrator=change
            db.session.add(user)
            db.session.commit()
            print(f'{e}: user.administrator={user.administrator}')
            sys.stdout.flush()


def change_private_routes(route , change, emails=None, domain=None):
    route_obj=PrivateRoutes.query.filter_by(route=route).first()
    if not route_obj:
        route_obj=PrivateRoutes(route=route)

    if domain :
        if not route_obj.users_domains :
            route_obj.users_domains=[]
        if change:
            route_obj.users_domains=list(set(route_obj.users_domains+[domain]))
        else:
            route_obj.users_domains=[ s for s in route_obj.users_domains if s != domain ]
        db.session.add(route_obj)
        db.session.commit()
        print(f'{route}: route.users_domains={", ".join(route_obj.users_domains)}')
        sys.stdout.flush()
        return None

    if emails:
        if not route_obj.users :
            route_obj.users=[]
        emails=",".join(emails)
        emails=emails.replace(" ", "")
        uids=[]
        for e in emails.split(","):
            user=User.query.filter_by(email=e).first()
            if not user:
                print(e, "could not be found!" )
                sys.stdout.flush()
            else:
                if not user.user_myapps:
                    user.user_myapps=[]
                if change:
                    route_obj.users=list(set(route_obj.users+[ user.id ]))
                    user.user_myapps=list(set(user.user_myapps+[ route_obj.id ]))
                else:
                    route_obj.users=[ s for s in route_obj.users if s != user.id ]
                    user.user_myapps=[ s for s in user.user_myapps if s != route_obj.id ]
                db.session.add(user)
                db.session.commit()
                uids.append(user.id)
                print(f'{user.email}: {", ".join([ PrivateRoutes.query.filter_by(id=i).first().route for i in user.user_myapps ] )}')
                sys.stdout.flush()
        if change:
            route_obj.users=list(set(route_obj.users+uids))
        else:
            route_obj.users=[ s for s in route_obj.users if s not in uids ]
        db.session.add(route_obj)
        db.session.commit()
        print(f'{route}: {", ".join([ User.query.filter_by(id=i).first().email for i in route_obj.users ] )}')
        sys.stdout.flush()
        
        return None
                
if __name__ == "__main__":

    with app.app_context():
        if sys.argv[1] not in ["admin","routes","status"]:
            parser = argparse.ArgumentParser(description='Manage your flaskapp.')
            parser.add_argument('function', type=str, nargs='?', choices=["admin","routes","status"], help='Choose your main function. opts=["admin","routes"]')
            args = parser.parse_args()

        if sys.argv[1] == "admin":
            parser = argparse.ArgumentParser(description="Grant or revoke administrator rights.")
            parser.add_argument('admin', metavar="admin", type=str, nargs='?', choices=["admin"])
            parser.add_argument('--add', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to grant rights to eg. john@gmail.com andre@netflix.com")
            parser.add_argument('--rm', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to revoke rights to eg. john@gmail.com andre@netflix.com")
            args = parser.parse_args()

            if (not args.add) and ( not args.rm):
                print("Please use --add or --rm")
            if args.add:
                change_admin(args.add,True)
            if args.rm:
                change_admin(args.rm,False)
            sys.stdout.flush()
            sys.exit(0)

        if sys.argv[1] == "routes":
            parser = argparse.ArgumentParser(description="Add users and domains to private routes.")
            parser.add_argument('routes', metavar="routes", type=str, nargs='?', choices=["routes"])
            parser.add_argument('--route', metavar="route", type=str, nargs='?',  choices=PRIVATE_ROUTES, help=f'Route to work on options: {", ".join(PRIVATE_ROUTES)}')
            parser.add_argument('--add-email', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to grant rights to eg. john@gmail.com andre@netflix.com")
            parser.add_argument('--rm-email', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to revoke rights to eg. john@gmail.com andre@netflix.com")
            parser.add_argument('--add-domain', metavar="gmail.com", type=str, nargs='?', help="Domain to grant rights to eg. gmail.com")
            parser.add_argument('--rm-domain', metavar="gmail.com", type=str, nargs='?', help="Domain to revoke rights to eg. gmail.com")
            args = parser.parse_args()

            if (not args.add_email ) and ( not args.add_domain ) and (not args.rm_email ) and ( not args.rm_domain ) :
                print("Please use either --add-email or --rm-email or --add-domain or --rm-domain")
            if args.add_email:
                change_private_routes( args.route, True, emails=args.add_email)
            if args.rm_email:
                change_private_routes( args.route, False, emails=args.rm_email)
            if args.add_domain:
                change_private_routes( args.route, True, domain=args.add_domain)
            if args.rm_domain:
                change_private_routes( args.route, False, domain=args.rm_domain)
            sys.stdout.flush()
            sys.exit(0)

        if sys.argv[1] == "status":
            parser = argparse.ArgumentParser(description="Grant or revoke administrator rights.")
            parser.add_argument('status', metavar="status", type=str, nargs='?', choices=["status"])
            parser.add_argument('--add', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to activate eg. john@gmail.com andre@netflix.com")
            parser.add_argument('--rm', metavar="email@gmail.com", type=str, nargs='*', help="Emails of users to deactivate eg. john@gmail.com andre@netflix.com")
            args = parser.parse_args()

            if (not args.add) and ( not args.rm):
                print("Please use --add or --rm")
            if args.add:
                change_active_status(args.add,True)
            if args.rm:
                change_active_status(args.rm,False)
            sys.stdout.flush()
            sys.exit(0)
